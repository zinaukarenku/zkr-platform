from celery import shared_task

from questions.models import Question, QuestionStatus, PoliticianAnswer
from web.sendgrid import SendGrid


@shared_task(soft_time_limit=30)
def send_question_accepted_letter(question_id=None):
    questions = Question.active.filter(is_moderator_decision_letter_sent=False)

    if question_id:
        questions = questions.filter(pk=question_id)

    letters_sent = []
    for question in questions:
        email = question.question_author_email

        SendGrid().send_letter(
            template_id=SendGrid.QUESTION_ACCEPTED_TRANSACTIONAL_TEMPLATE,
            emails=[email],
            dynamic_template_data={
                'question_title': question.name,
                'question_url': question.get_absolute_url(),
            },
            categories=[SendGrid.CATEGORY_QUESTIONS_AND_ANSWERS]
        )

        letters_sent.append(email)

        question.is_moderator_decision_letter_sent = True
        question.save(update_fields=['is_moderator_decision_letter_sent'])

    return letters_sent


@shared_task(soft_time_limit=30)
def send_question_rejected_letter(question_id=None):
    questions = Question.objects.filter(status=QuestionStatus.REJECTED).filter(is_moderator_decision_letter_sent=False)

    if question_id:
        questions = questions.filter(pk=question_id)

    letters_sent = []
    for question in questions:
        email = question.question_author_email

        SendGrid().send_letter(
            template_id=SendGrid.QUESTION_REJECTED_TRANSACTIONAL_TEMPLATE,
            emails=[email],
            dynamic_template_data={
                'question_title': question.name,
                'question_url': question.get_absolute_url(),
                'question_rejected_reason': question.rejected_reason
            },
            categories=[SendGrid.CATEGORY_QUESTIONS_AND_ANSWERS]
        )

        letters_sent.append(email)

        question.is_moderator_decision_letter_sent = True
        question.save(update_fields=['is_moderator_decision_letter_sent'])

    return letters_sent


@shared_task(soft_time_limit=30)
def send_question_answered_letter(answer_id=None):
    answers = PoliticianAnswer.objects.select_related('question').filter(is_question_answered_letter_sent=False)

    if answer_id:
        answers = answers.filter(pk=answer_id)

    letters_sent = []
    for answer in answers:
        question = answer.question
        email = question.question_author_email

        SendGrid().send_letter(
            template_id=SendGrid.QUESTION_ANSWERED_TRANSACTIONAL_TEMPLATE,
            emails=[email],
            dynamic_template_data={
                'question_title': question.name,
                'question_url': question.get_absolute_url(),
            },
            categories=[SendGrid.CATEGORY_QUESTIONS_AND_ANSWERS]
        )

        letters_sent.append(email)

        answer.is_question_answered_letter_sent = True
        answer.save(update_fields=['is_question_answered_letter_sent'])

    return letters_sent


@shared_task(soft_time_limit=30)
def send_new_question_for_politician_letter(question_id=None, force_send=False):
    questions = Question.active.select_related('politician').exclude_answered_questions()
    if not force_send:
        questions = questions.filter(is_letter_for_politician_sent=False)

    if question_id:
        questions = questions.filter(pk=question_id)

    letters_sent = []
    for question in questions:
        contact_emails = question.politician.contact_emails
        if len(contact_emails) == 0:
            continue

        SendGrid().send_letter(
            template_id=SendGrid.QUESTION_FOR_POLITICIAN_TRANSACTIONAL_TEMPLATE,
            emails=contact_emails,
            dynamic_template_data={
                'question_title': question.name,
                'question_url': question.get_editable_absolute_url_for_politician(),
            },
            categories=[SendGrid.CATEGORY_QUESTIONS_AND_ANSWERS]
        )

        letters_sent.extend(contact_emails)

        question.is_letter_for_politician_sent = True
        question.save(update_fields=['is_letter_for_politician_sent'])

    return letters_sent
