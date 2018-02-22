import os

from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from django.core.files import File

from odin.users.factories import ProfileFactory

from odin.education.factories import (
    StudentFactory,
    CourseFactory,
    TopicFactory,
    ProgrammingLanguageFactory,
)
from odin.education.services import add_student, create_included_task, create_test_for_task


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        language = ProgrammingLanguageFactory(name='java')

        competition = CourseFactory(
            name='HackConf Competition',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            #is_competition=True
        )

        # assert competition.is_competition

        student = StudentFactory(
            email='teststudent@hacksoft.io',
            password='teststudent',
        )
        student.is_active = True
        student.save()

        ProfileFactory(
            full_name='Test Student',
            user=student.user
        )

        add_student(course=competition, student=student)

        week = competition.weeks.first()
        topic = TopicFactory(
            name='Problems',
            course=competition,
            week=week
        )
        task = create_included_task(
            name='String Encoding',
            description='Some string encoding',
            gradable=True,
            topic=topic
        )

        test_file_path = os.path.join(
            str(settings.ROOT_DIR),
            'odin',
            'education',
            'management',
            'commands',
            'competition_task_tests.tar.gz'
        )
        test_file = open(test_file_path, 'rb')

        test = create_test_for_task(
            task=task,
            language=language,
            extra_options={
                'archive_test_type': 'tar_gz',
                'class_name': 'Solution'
            },
            code='temp'
        )

        test.code = None
        test.file.save('test.tar.gz', File(test_file))
        test.full_clean()
        test.save()
        task.save()

        print('Competition created.')
