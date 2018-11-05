from gettext import gettext

from django.apps import AppConfig


class QuestionsConfig(AppConfig):
    name = 'questions'
    verbose_name = gettext("Klausimai politikams")
