from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'odin.users'

    def ready(self):
        import odin.users.signals
