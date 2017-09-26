from copy import deepcopy

import factory

from django.utils import timezone

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory
from odin.education.factories import MaterialFactory, TopicFactory, TaskFactory

from .models import (
    CompetitionParticipant,
    CompetitionJudge,
    Competition,
    CompetitionMaterial,
    CompetitionTask
)


class CompetitionParticipantFactory(BaseUserFactory):
    class Meta:
        model = CompetitionParticipant


class CompetitionJudgeFactory(BaseUserFactory):
    class Meta:
        model = CompetitionJudge


class CompetitionFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'{n}{faker.word()}')
    start_date = factory.LazyAttribute(lambda _: timezone.now().date() + timezone.timedelta(days=faker.pyint()))

    slug_url = factory.Sequence(lambda n: f'{n}{faker.slug()}')

    repository = factory.LazyAttribute(lambda _: faker.url())
    video_channel = factory.LazyAttribute(lambda _: faker.url())
    facebook_group = factory.LazyAttribute(lambda _: faker.url())

    class Meta:
        model = Competition

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        new_kwargs = deepcopy(kwargs)
        if not kwargs.get('end_date'):
            end_date = kwargs.get('start_date') + timezone.timedelta(days=faker.pyint())
            new_kwargs['end_date'] = end_date
        obj = model_class(**new_kwargs)
        obj.save()
        return obj


class CompetitionMaterialFactory(factory.DjangoModelFactory):
    material = factory.SubFactory(MaterialFactory)
    topic = factory.SubFactory(TopicFactory)

    class Meta:
        model = CompetitionMaterial


class CompetitionTaskFactory(factory.DjangoModelFactory):
    task = factory.SubFactory(TaskFactory)
    topic = factory.SubFactory(TopicFactory)

    class Meta:
        model = CompetitionTask
