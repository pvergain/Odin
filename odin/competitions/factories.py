from copy import deepcopy

import factory

from django.utils import timezone

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory
from odin.education.factories import MaterialFactory, TaskFactory, TaskTestFactory

from .models import (
    CompetitionParticipant,
    CompetitionJudge,
    Competition,
    CompetitionMaterial,
    CompetitionTask,
)
from .services import (
    create_competition_test,
    create_competition_material,
    create_competition_task
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
    competition = factory.SubFactory(CompetitionFactory)

    class Meta:
        model = CompetitionMaterial

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        material = kwargs.get('material')
        fields = ('identifier', 'url', 'content')
        for field in fields:
            if not kwargs.get(field):
                kwargs[field] = material.__dict__.get(field)
        kwargs['existing_material'] = kwargs.pop('material')
        return create_competition_material(*args, **kwargs)


class CompetitionTaskFactory(factory.DjangoModelFactory):
    task = factory.SubFactory(TaskFactory)
    competition = factory.SubFactory(CompetitionFactory)

    class Meta:
        model = CompetitionTask

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        task = kwargs.get('task')
        fields = ('name', 'description', 'gradable')
        for field in fields:
            if not kwargs.get(field):
                kwargs[field] = task.__dict__.get(field)
        kwargs['existing_task'] = kwargs.pop('task')
        return create_competition_task(*args, **kwargs)


class CompetitionTestFactory(TaskTestFactory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs['code'] = faker.text()
        return create_competition_test(*args, **kwargs)
