from django.apps import AppConfig


class FandomsConfig(AppConfig):
    name = 'fandoms'

    def ready(self):
        import fandoms.signals
