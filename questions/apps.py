from django.utils.translation import gettext_lazy as _

from django.apps import AppConfig


class QuestionsConfig(AppConfig):
    name = 'questions'
    verbose_name = _("Klausimai politikams")
