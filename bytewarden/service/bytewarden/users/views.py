from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import login
from questions.models import Question
from users.models import CustomUser as User
from bytewarden.utils import filter_parameter, UserSignUpForm


def home(request):
	return render(request,"users/home.html")

class SignUp(CreateView):
	form_class = UserSignUpForm
	success_url = reverse_lazy("login")
	template_name = "registration/signup.html"


def recover(request):
	context = {}

	if request.method == "GET":
		try:
			num = filter_parameter(request.GET.get("num"))
			username = request.GET.get("username")

			if not username:
				return render(request,"users/recover.html")

			context["username"] = username
			question = Question.objects.get(user = User.objects.get(username = username), question_num = num)
			context["question"] = question

			return render(request,"users/recover.html", context)

			
		except (KeyError, User.DoesNotExist, Question.DoesNotExist) as e:
			context["error_message"] = "Username or Question does not exist"
			return render(request,"users/recover.html", context)

	try:
		num = filter_parameter(request.POST.get("num"))
		username = request.POST.get("username")
		answer = request.POST.get("answer")

		context["username"] = username
		question = Question.objects.get(user = User.objects.get(username = username), question_num = num)
		context["question"] = question

		if not answer:
			return render(request,"users/recover.html", context)
		
		if question.answer_text == answer:
			user = User.objects.get(username = username)
			login(request, user)
			user.used_recovery_login = True
			user.save()
			return redirect("home")
		else:
			context["error_message"] = "Your Answer to the Question is incorrect"
			return render(request, "users/recover.html", context)

		
	except (KeyError, User.DoesNotExist, Question.DoesNotExist) as e:
		context["error_message"] = "Username or Question does not exist"
		return render(request,"users/recover.html", context)

