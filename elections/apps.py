from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ElectionsConfig(AppConfig):
    name = 'elections'
    verbose_name = _("Rinkimai")
