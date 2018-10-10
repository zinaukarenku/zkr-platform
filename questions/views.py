from django.shortcuts import render

from questions.forms import NewQuestionForm
from questions.models import Question
from zkr.utils import request_country, request_user_agent, request_ip


def index(request):
    return render(request, 'seimas/index.html')


def new_question(request):
    # TODO Redirect if user is not logged in

    user = request.user
    user_ip = request_ip(request)
    user_agent = request_user_agent(request)
    user_country = request_country(request)

    question = Question(created_by=user, user_ip=user_ip, user_agent=user_agent, user_country=user_country)

    new_question_form = NewQuestionForm(instance=question)
    success = None

    if request.method == 'POST':
        success = False
        new_question_form = NewQuestionForm(request.POST, instance=question)

        if new_question_form.is_valid():
            new_question_form.save()
            success = True

    return render(request, 'questions/new-question.html', {
        'new_question_form': new_question_form,
        'success': success
    })
