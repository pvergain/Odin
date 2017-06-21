from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    name = 'odin.authentication'

    def ready(self):
        import odin.authentication.signals  # noqa
