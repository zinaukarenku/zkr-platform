from django.db.models.signals import post_save
from django.dispatch import receiver

from questions.tasks import send_question_accepted_letter, send_question_rejected_letter, send_question_answered_letter
from questions.models import Question, PoliticianAnswer


@receiver(post_save, sender=Question)
def on_question_saved(sender, instance, **kwargs):
    question_id = instance.pk

    send_question_accepted_letter.delay(question_id)
    send_question_rejected_letter.delay(question_id)


@receiver(post_save, sender=PoliticianAnswer)
def on_politician_answer_saved(sender, instance, **kwargs):
    send_question_answered_letter.delay(instance.pk)
