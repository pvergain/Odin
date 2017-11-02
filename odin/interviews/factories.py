import factory

from django.utils import timezone

from odin.common.faker import faker
from odin.applications.factories import ApplicationFactory
from odin.users.factories import BaseUserFactory

from .models import Interview, Interviewer, InterviewerFreeTime


class InterviewerFactory(BaseUserFactory):
    skype = factory.LazyAttribute(lambda _: faker.name())

    class Meta:
        model = Interviewer


class InterviewerFreeTimeFactory(factory.DjangoModelFactory):
    interviewer = factory.SubFactory(InterviewerFactory)
    date = factory.LazyAttribute(lambda _:  timezone.now().date() + timezone.timedelta(days=faker.pyint()))
    start_time = factory.LazyAttribute(lambda _: timezone.now().time())
    end_time = factory.LazyAttribute(lambda _: (timezone.now() + timezone.timedelta(minutes=20)).time())

    class Meta:
        model = InterviewerFreeTime


class InterviewFactory(factory.DjangoModelFactory):
    interviewer = factory.SubFactory(InterviewerFactory)
    application = factory.SubFactory(ApplicationFactory)
    date = factory.LazyAttribute(lambda _: faker.date_object())
    start_time = factory.LazyAttribute(lambda _: faker.time_object())
    end_time = factory.LazyAttribute(lambda _: faker.time_object())
    interviewer_time_slot = factory.SubFactory(InterviewerFreeTimeFactory)
    uuid = factory.LazyAttribute(lambda _: faker.uuid4())
    interviewer_comment = factory.LazyAttribute(lambda _: faker.text())

    class Meta:
        model = Interview
