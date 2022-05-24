from django.http import QueryDict, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Question
from bytewarden.utils import filter_parameter

def get_question_indices(questions):
	if len(questions) <= 0:
		return None
	
	return range(1, len(questions)+1)

@login_required()
def questions(request):

	# TODO:
	# Unneeded functionality, like resetting questions, ...

	# make gameserver use forgot password and shared questions !!!

	questions = Question.objects.filter(user = request.user)
	context = {"question_range" : get_question_indices(questions)}

	if len(questions) > 0:
		question_range = range(1, len(questions)+1)
		context["question_range"] = question_range

	if request.method == "GET":
		try:
			if request.GET.get("num"):
				num = filter_parameter(request.GET.get("num"))	
				context["question"] = questions.get(question_num = num)

		except Question.DoesNotExist:
			context["error_message"] = f"Question {num} does not exist"
		
		finally:
			return render(request, "questions/questions.html", context)

	if request.user.used_recovery_login:
		context["error_message"] = "Cannot Add/Edit Question when logged in through recovery!"
		return render(request, "questions/questions.html", context)

	try:
		num = filter_parameter(request.POST.get("num"))
		new_question = request.POST.get("new_question")
		new_answer = request.POST.get("new_answer")
		is_shared = request.POST.get("is_shared")

		question, _ = Question.objects.get_or_create(user = request.user, question_num = num)

		question.question_text = new_question
		question.answer_text = new_answer
		if is_shared:
			question.is_shared = True
		question.save()

		context["question"] = question

		return redirect("questions:questions")

	except (KeyError, Question.DoesNotExist):
		context["error_message"] = "Question does not exist or invalid parameters"
		return render(request, "questions/questions.html", context)


@login_required()
def reset(request):
	questions = Question.objects.filter(user = request.user)
	if request.user.used_recovery_login:
		context  = {
			"question_range" : get_question_indices(questions),
			"error_message" : "Cannot reset Questions when logged in through recovery!",
			}
		return render(request, "questions/questions.html", context)
	questions.delete()
	return render(request, "questions/questions.html")


@login_required()
def shared_questions(request):
	context = {
			"questions": Question.objects.filter(is_shared = True)
			}
	return render(request, "questions/common_questions.html", context)