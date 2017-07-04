import os

from django.core.management import call_command
from django.conf import settings
from django.db import connection
from io import StringIO


from allauth.socialaccount.providers.oauth2 import views
from django.core.management import call_command
from django.core.management.base import BaseCommand

from odin.common.load_data import (
    CourseLoader,
    TeacherLoader,
    StudentLoader,
    BaseUserLoader,
    ProfileLoader,
    CourseAssignmentLoader,
    TopicLoader,
    IncludedMaterialLoader,
)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        loaders = [
            BaseUserLoader(),
            ProfileLoader(),
            CourseLoader(),
            TeacherLoader(),
            StudentLoader(),
            CourseAssignmentLoader(),
            TopicLoader(),
            IncludedMaterialLoader()
        ]

        for loader in loaders:
            loader.generate_orm_objects()

        commands = StringIO()
        cursor = connection.cursor()

        for app in settings.LOCAL_APPS:
            label = app.split('.')[1]
            os.system(f'python manage.py sqlsequencereset {label} | python manage.py dbshell')
