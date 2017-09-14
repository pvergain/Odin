import os

from django.conf import settings

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
    ProgrammingLanguageLoader,
    IncludedTaskLoader,
    IncludedTestLoader,
    SolutionLoader,
    LectureLoader
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
            IncludedMaterialLoader(),
            ProgrammingLanguageLoader(),
            IncludedTaskLoader(),
            IncludedTestLoader(),
            SolutionLoader(),
            LectureLoader()
        ]

        for loader in loaders:
            print(f'Generating {loader.__class__.__name__}')
            loader.generate_orm_objects()

        for app in settings.LOCAL_APPS:
            label = app.split('.')[1]
            os.system(f'python manage.py sqlsequencereset {label} | python manage.py dbshell')
