import factory

from odin.common.faker import faker
from odin.education.factories import CourseFactory
from odin.users.factories import BaseUserFactory
from .models import Application, ApplicationInfo


class ApplicationInfoFactory(factory.DjangoModelFactory):
    start_date = factory.LazyAttribute(lambda _: faker.date_object())
    end_date = factory.LazyAttribute(lambda _: faker.date_object())
    course = factory.SubFactory(CourseFactory)
    start_interview_date = factory.LazyAttribute(lambda _: faker.date_object())
    end_interview_date = factory.LazyAttribute(lambda _: faker.date_object())
    description = factory.LazyAttribute(lambda _: faker.text())

    class Meta:
        model = ApplicationInfo


class ApplicationFactory(factory.DjangoModelFactory):
    application_info = factory.SubFactory(ApplicationInfoFactory)
    user = factory.SubFactory(BaseUserFactory)
    phone = factory.LazyAttribute(lambda _: faker.phone_number())
    skype = factory.LazyAttribute(lambda _: faker.word())

    class Meta:
        model = Application
