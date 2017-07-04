import factory

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory

from .models import Student, Teacher, Course, Week, Topic, Material, IncludedMaterial
from .services import create_course


class StudentFactory(BaseUserFactory):
    class Meta:
        model = Student


class TeacherFactory(BaseUserFactory):
    class Meta:
        model = Teacher


class CourseFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(lambda _: faker.word())
    start_date = factory.LazyAttribute(lambda _: faker.date_object())
    end_date = factory.LazyAttribute(lambda _: faker.date_object())

    slug_url = factory.LazyAttribute(lambda _: faker.slug())

    repository = factory.LazyAttribute(lambda _: faker.url())
    video_channel = factory.LazyAttribute(lambda _: faker.url())
    facebook_group = factory.LazyAttribute(lambda _: faker.url())

    class Meta:
        model = Course

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return create_course(*args, **kwargs)


class WeekFactory(factory.DjangoModelFactory):
    number = factory.LazyAttribute(lambda _: faker.pyint())

    start_date = factory.LazyAttribute(lambda _: faker.date_object())
    end_date = factory.LazyAttribute(lambda _: faker.date_object())

    course = factory.SubFactory(CourseFactory)

    class Meta:
        model = Week


class TopicFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(lambda _: faker.name())
    course = factory.SubFactory(CourseFactory)
    week = factory.SubFactory(WeekFactory)

    class Meta:
        model = Topic


class MaterialFactory(factory.DjangoModelFactory):
    identifier = factory.LazyAttribute(lambda _: faker.word())
    url = factory.LazyAttribute(lambda _: faker.url())
    content = factory.LazyAttribute(lambda _: faker.text())

    class Meta:
        model = Material


class IncludedMaterialFactory(factory.DjangoModelFactory):
    material = factory.SubFactory(MaterialFactory)
    topic = factory.SubFactory(TopicFactory)

    class Meta:
        model = IncludedMaterial
