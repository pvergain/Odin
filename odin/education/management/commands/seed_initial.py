from django.core.management.base import BaseCommand

from random import choice
from queue import deque
from allauth.account.models import EmailAddress

from odin.users.factories import SuperUserFactory

from odin.education.factories import (
    StudentFactory,
    TeacherFactory,
    CourseFactory,
    TopicFactory,
    WeekFactory,
    TaskFactory,
    IncludedTaskFactory,
    ProgrammingLanguageFactory,
    SourceCodeTestFactory,
)
from odin.education.services import add_student, add_teacher


COURSE_NAMES = ("Python 101", "Ruby 101", "Java 101")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        courses = [CourseFactory(name=name) for name in COURSE_NAMES]
        teachers = deque(TeacherFactory.create_batch(6))
        students = deque(StudentFactory.create_batch(40))

        while teachers:
            selected_course = choice(courses)
            add_teacher(selected_course, teachers.popleft())

        while students:
            selected_course = choice(courses)
            add_student(selected_course, students.popleft())

        weeks = deque()

        for course in courses:
            for i in range(10):
                weeks.appendleft(WeekFactory(course=course))

        topics = deque()
        while weeks:
            week = weeks.popleft()
            topics.appendleft(TopicFactory(week=week, course=week.course))

        tasks = deque()
        while topics:
            topic = topics.popleft()
            task = TaskFactory()
            tasks.appendleft(IncludedTaskFactory(task=task, topic=topic))

        language = ProgrammingLanguageFactory(name='python')

        while tasks:
            task = tasks.popleft()

            if task.gradable:
                SourceCodeTestFactory(task=task, language=language)

        email = 'testadmin@hacksoft.io'
        password = 'asdf'

        # verify email for allauth so it doesn't want email confirmation
        superuser = SuperUserFactory(email=email, password=password)
        EmailAddress.objects.create(user=superuser, email=email, primary=True, verified=True)

        print(f'Superuser created: {email}/{password}')
