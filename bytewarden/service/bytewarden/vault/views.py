from django.shortcuts import redirect
from django.template.response import TemplateResponse as render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from .utils import set_code, get_pow_prefix, pow_valid, two_factor_match
from .models import Password
from bytewarden.settings import POW_DIFFICULTY, TWOFA_LENGTH


# TODO edit password how?
# TODO through recovery only read access (cant edit 2fa code, questions, passwords)

@login_required()
@permission_required("vault.view_password", raise_exception=True)
def show_passwords(request):
	passwords = Password.objects.filter(user = request.user)
	context = { "passwords" : passwords }

	if request.method == "GET":
		return render(request, "vault/passwords.html", context)

	if request.user.used_recovery_login:
		context["error_message"] = "Cannot add Password when logged in through recovery!"
		return render(request, "vault/passwords.html", context)

	try:
		p = Password(
				password_num = len(passwords) + 1,
				user = request.user,
				title = request.POST.get("add_title"),
				url = request.POST.get("add_url"),
				password = request.POST.get("add_pwd"),
			)
		p.save()
		context["passwords"] = list(passwords).append(p)

		return redirect("vault:passwords")

	except (KeyError):
		context["error_message"] = "Not sufficient or invalid parameters to create a Password."
		return render(request, "vault/passwords.html", context)


@login_required()
@permission_required("vault.view_password", raise_exception=True)
def purge_passwords(request):
	passwords = Password.objects.filter(user = request.user)
	if request.user.used_recovery_login:
		context = { 
			"passwords" : passwords,
			"error_message" : "Cannot delete Passwords when logged in through recovery!",
			}
		return render(request, "vault/passwords.html", context)
	
	passwords.delete()
	return redirect("vault:passwords")


@login_required()
@permission_required("vault.view_password", raise_exception=True)
def reset_2fa(request):
	if request.user.used_recovery_login:
		context = { 
			"passwords" : Password.objects.filter(user = request.user),
			"error_message" : "Cannot reset 2FA Code when logged in through recovery!",
			}
		return render(request, "vault/passwords.html", context)
	set_code(request.user)
	return redirect("home")


@login_required()
def two_factor_auth(request):
	context = { 
		"2fa_length" : TWOFA_LENGTH,
		"pow_difficulty" : POW_DIFFICULTY,
	}
	
	if request.user.code == "":
		set_code(request.user)
		return render(request, "vault/first_visit.html", context)

	if request.method == "GET":
		request.session["pow_prefix"] = get_pow_prefix()
		context["pow_prefix"] = request.session["pow_prefix"]
		return render(request, "vault/two_factor_auth.html", context)

	c_code = request.POST.get("2fa_code")
	pow_str = request.POST.get("pow")

	old_pow_prefix = request.session.pop("pow_prefix")
	context["pow_prefix"] = request.session["pow_prefix"] = get_pow_prefix()

	if two_factor_match(request.user.code, c_code) and pow_valid(old_pow_prefix, pow_str):
		request.user.user_permissions.add(Permission.objects.get(codename="view_password"))
		return redirect("vault:passwords")
	else:
		context["error_message"] = "Wrong 2FA Code or PoW" #+ request.user.code # TODO remove code
		
		resp = render(request, "vault/two_factor_auth.html", context)
		if not pow_valid(old_pow_prefix, pow_str):
			resp["DebugStats"] = "PoW invalid!"

		return resp