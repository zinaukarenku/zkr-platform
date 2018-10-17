from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from questions.forms import NewQuestionForm
from questions.models import Question
from utils.utils import get_request_information


def index(request):
    return render(request, 'seimas/index.html')


@login_required
def new_question(request):
    user = request.user
    request_info = get_request_information(request)

    question = Question(
        created_by=user,
        user_ip=request_info.client_ip,
        user_agent=request_info.client_user_agent,
        user_country=request_info.client_country
    )

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
