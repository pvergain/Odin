from django.apps import AppConfig


class InterviewsConfig(AppConfig):
    name = 'odin.interviews'

    def ready(self):
        import odin.interviews.signals  # noqa
