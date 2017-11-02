from django.apps import AppConfig


class CompetitionsConfig(AppConfig):
    name = 'odin.competitions'

    def ready(self):
        import odin.competitions.signals # noqa
