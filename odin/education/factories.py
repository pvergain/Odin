import factory

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory

from .models import Student, Teacher, Course


class StudentFactory(BaseUserFactory):
    class Meta:
        model = Student


class TeacherFactory(BaseUserFactory):
    class Meta:
        model = Teacher


class CourseFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(lambda _: faker.word())
    start_date = factory.LazyAttribute(lambda _: faker.date())
    end_date = factory.LazyAttribute(lambda _: faker.date())

    """
    TODO:
    1) Add fields for rest of the model fields
    """

    class Meta:
        model = Course
