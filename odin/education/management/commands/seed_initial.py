from django.core.management.base import BaseCommand

from random import choice
from queue import deque

from ...models import Course, Student, Teacher
from ...factories import StudentFactory, TeacherFactory, CourseFactory

COURSE_NAMES = ("Python 101", "Ruby 101", "Java 101")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        courses = [CourseFactory(name=name) for name in COURSE_NAMES]
        teachers = deque(TeacherFactory.create_batch(6))
        students = deque(StudentFactory.create_batch(40))

        while teachers:
            selected_course = choice(courses)
            selected_course.add_teacher(teachers.popleft())

        while students:
            selected_course = choice(courses)
            selected_course.add_student(students.popleft())
