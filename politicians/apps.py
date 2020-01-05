from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PoliticiansConfig(AppConfig):
    name = 'politicians'
    verbose_name = _("Politikų Olimpas")

    def ready(self):
        # noinspection PyUnresolvedReferences
        import politicians.signals

