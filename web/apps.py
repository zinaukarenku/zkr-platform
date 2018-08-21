from django.apps import AppConfig


class WebConfig(AppConfig):
    name = 'web'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import web.signals
