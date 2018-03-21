from django.apps import AppConfig


class EmailsConfig(AppConfig):
    name = 'odin.emails'

    def ready(self):
        import odin.emails.tasks  # noqa
