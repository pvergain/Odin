import factory

from django.utils import timezone

from odin.common.faker import faker
from odin.education.factories import CourseFactory
from odin.users.factories import BaseUserFactory
from .models import (
    Application,
    ApplicationInfo,
    ApplicationTask,
    IncludedApplicationTask,
    ApplicationSolution
)


class ApplicationInfoFactory(factory.DjangoModelFactory):
    start_date = factory.LazyAttribute(lambda _: timezone.now().date() + timezone.timedelta(days=faker.pyint()))
    end_date = factory.LazyAttribute(lambda _: timezone.now().date() + timezone.timedelta(days=faker.pyint()))
    course = factory.SubFactory(CourseFactory)
    start_interview_date = factory.LazyAttribute(lambda _: timezone.now().date() +
                                                 timezone.timedelta(days=faker.pyint()))
    end_interview_date = factory.LazyAttribute(lambda _: timezone.now().date() + timezone.timedelta(days=faker.pyint()))
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


class ApplicationTaskFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'{n}{faker.word()}')
    description = factory.LazyAttribute(lambda _: faker.text())
    gradable = factory.LazyAttribute(lambda _: faker.boolean())

    class Meta:
        model = ApplicationTask


class IncludedApplicationTaskFactory(factory.DjangoModelFactory):
    application_info = factory.SubFactory(ApplicationInfoFactory)
    task = factory.SubFactory(ApplicationTaskFactory)

    class Meta:
        model = IncludedApplicationTask


class ApplicationSolutionFactory(factory.DjangoModelFactory):
    task = factory.SubFactory(IncludedApplicationTaskFactory)
    application = factory.SubFactory(ApplicationFactory)
    url = factory.LazyAttribute(lambda _: faker.url())

    class Meta:
        model = ApplicationSolution
