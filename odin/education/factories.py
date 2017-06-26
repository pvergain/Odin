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

    slug_url = factory.LazyAttribute(lambda _: faker.word())

    repository = factory.LazyAttribute(lambda _: faker.url())
    video_channel = factory.LazyAttribute(lambda _: faker.url())
    facebook_group = factory.LazyAttribute(lambda _: faker.url())

    class Meta:
        model = Course
