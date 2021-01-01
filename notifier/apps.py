from django.apps import AppConfig


class NotifierConfig(AppConfig):
    name = 'notifier'

    def ready(self):
        import notifier.signals
