import factory

from django.utils import timezone

from odin.common.faker import faker
from odin.education.factories import CourseFactory
from odin.users.factories import BaseUserFactory
from odin.competitions.factories import CompetitionFactory
from .models import (
    Application,
    ApplicationInfo,
)


class ApplicationInfoFactory(factory.DjangoModelFactory):
    start_date = factory.LazyAttribute(lambda _: timezone.now().date() + timezone.timedelta(days=faker.pyint()))
    end_date = factory.LazyAttribute(lambda _: timezone.now().date() + timezone.timedelta(days=faker.pyint()))
    course = factory.SubFactory(CourseFactory)
    start_interview_date = factory.LazyAttribute(lambda _: timezone.now().date() +
                                                 timezone.timedelta(days=faker.pyint()))
    end_interview_date = factory.LazyAttribute(lambda _: timezone.now().date() + timezone.timedelta(days=faker.pyint()))
    description = factory.LazyAttribute(lambda _: faker.text())
    competition = factory.SubFactory(CompetitionFactory)

    class Meta:
        model = ApplicationInfo


class ApplicationFactory(factory.DjangoModelFactory):
    application_info = factory.SubFactory(ApplicationInfoFactory)
    user = factory.SubFactory(BaseUserFactory)
    phone = factory.LazyAttribute(lambda _: faker.phone_number())
    skype = factory.LazyAttribute(lambda _: faker.word())

    class Meta:
        model = Application
