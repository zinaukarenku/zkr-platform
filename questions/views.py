import reversion
from allauth.account.decorators import verified_email_required
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import redirect, render

from questions.forms import NewQuestionForm, PoliticianAnswerFormSet
from questions.models import Question
from utils.utils import get_request_information
from web.models import PoliticianInfo


def questions_list(request):
    questions = Question.active.select_related('politician', 'politian_answer', 'created_by') \
        .annotate(last_created_at=Coalesce('politian_answer__created_at', 'created_at')) \
        .order_by('-last_created_at')

    return render(
        request, 'questions/questions-list.html',
        {
            'questions': questions
        }
    )


@verified_email_required
def new_question(request, politician_id=None):
    user = request.user
    request_info = get_request_information(request)

    question = Question(
        created_by=user,
        user_ip=request_info.client_ip,
        user_agent=request_info.client_user_agent,
        user_country=request_info.client_country
    )

    selected_politician = PoliticianInfo.objects.filter(id=politician_id).first() if politician_id else None
    initial = {}

    if selected_politician:
        initial['politician'] = selected_politician

    new_question_form = NewQuestionForm(instance=question, initial=initial)
    success = None

    if request.method == 'POST':
        success = False
        new_question_form = NewQuestionForm(request.POST, instance=question)

        if new_question_form.is_valid():
            with reversion.create_revision():
                new_question_form.save()
            return redirect('question', question_id=question.id)

    return render(request, 'questions/new-question.html', {
        'new_question_form': new_question_form,
        'success': success
    })


@verified_email_required
def question_with_secret(request, question_id, secret_id):
    selected_question = Question.active.filter(id=question_id).first()

    if selected_question is None:
        raise Http404("Question does not exist")

    if not selected_question.has_politician_answer and selected_question.politician.registration_secret_id == secret_id:
        selected_question.politician.authenticated_users.add(request.user)

    return redirect('question', question_id)


def question(request, question_id):
    user = request.user
    request_info = get_request_information(request)

    selected_question = Question.active \
        .select_related('politician',
                        'politician__user',
                        'politian_answer',
                        'created_by') \
        .filter(id=question_id).first()

    if selected_question is None:
        selected_question = Question.objects.filter_questions_by_user(user) \
            .select_related('politician',
                            'politician__user',
                            'politian_answer',
                            'created_by') \
            .filter(id=question_id).first()

    if selected_question is None:
        raise Http404("Question does not exist")

    politician_answer_form = None
    if not selected_question.has_politician_answer and selected_question.is_question_for_user(user):
        politician_answer_form = PoliticianAnswerFormSet(instance=selected_question)

        if request.method == 'POST':
            politician_answer_form = PoliticianAnswerFormSet(request.POST, instance=selected_question)

            if politician_answer_form.is_valid():
                answers = politician_answer_form.save(commit=False)
                for answer in answers:
                    answer.created_by = user
                    answer.user_ip = request_info.client_ip
                    answer.user_agent = request_info.client_user_agent
                    answer.user_country = request_info.client_country
                    answer.save()

                politician_answer_form = None

    return render(request, 'questions/question.html', {
        'question': selected_question,
        'politician_answer_form': politician_answer_form,
    })
