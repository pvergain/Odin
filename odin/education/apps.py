from django.apps import AppConfig


class EducationConfig(AppConfig):
    name = 'odin.education'

    def ready(self):
        import odin.education.signals
