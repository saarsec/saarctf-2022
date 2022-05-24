from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from questions.models import Question, DEFAULT_QUESTIONS
from vault.utils import two_factor_match
from timeit import timeit, Timer
from datetime import datetime
from time import *
from users.models import CustomUser


DEFAULT_QUESTION_INDEX = 1
IS_SINGLE_DIGIT = lambda d: 0 <= int(d) < 10
DEBUG = True

def DisableCSRFMiddleware(get_response):

	def middleware(request):

		setattr(request, '_dont_enforce_csrf_checks', True)
		response = get_response(request)
		return response

	return middleware


class TimingMiddleware:

	def __init__(self, get_response):
		self.get_response = get_response


	def __call__(self, request):
		response = self.get_response(request)
		return response


	def process_template_response(self, request, response):

		if not request.user.is_authenticated or not DEBUG:
			return response

		if not response.get("DebugStats") and request.POST.get("2fa_code"):

			# TODO add in more places
			setup = \
			"from vault.utils import two_factor_match\n"\
			+ f"u_code = '{request.user.code}'\n"\
			+ f"p_code = '{request.POST.get('2fa_code')}'"

			diff = timeit("two_factor_match(u_code, p_code)", setup = setup, timer = thread_time_ns, number=10000)

			response["DebugStats"] = \
				f"Date and Time: {datetime.now().strftime('%Y-%m-%d, %H:%M:%S')};"\
			  + f"Password Check: {diff}ns;"\
			  + f"User: {request.user.username}, last login {request.user.last_login}, date joined {request.user.date_joined}"

		return response


def filter_parameter(string):

	if not string or not all(s.isdigit() for s in string):
		return DEFAULT_QUESTION_INDEX

	filtered = filter(IS_SINGLE_DIGIT, string)
	as_string = "".join(filtered)
		
	if as_string == "":
		return DEFAULT_QUESTION_INDEX

	return int(as_string)


class UserSignUpForm(UserCreationForm):

	def __init__(self, *args, **kwargs):
		super(UserSignUpForm, self).__init__(*args, **kwargs)
		del self.fields['password2']
		self.fields['username'].help_text = None
		self.fields['password1'].help_text = None

	
	class Meta:
		model = get_user_model()
		fields = ("username", "password1")


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
	user.used_recovery_login = False
	user.save()