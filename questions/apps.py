from django.utils.translation import gettext_lazy as _

from django.apps import AppConfig


class QuestionsConfig(AppConfig):
    name = 'questions'
    verbose_name = _("Klausimai / atsakymai politikams")

    def ready(self):
        # noinspection PyUnresolvedReferences
        import questions.signals
