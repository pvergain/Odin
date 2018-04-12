from copy import deepcopy

import factory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory

from odin.education.services import create_test_for_task

from .models import (
    Student,
    Teacher,
    Course,
    Week,
    Material,
    IncludedMaterial,
    Task,
    IncludedTask,
    ProgrammingLanguage,
    Test,
    Solution
)
from .services import create_course


class StudentFactory(BaseUserFactory):
    class Meta:
        model = Student


class TeacherFactory(BaseUserFactory):
    class Meta:
        model = Teacher


class CourseFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'{n}{faker.word()}')
    start_date = factory.LazyAttribute(lambda _: timezone.now().date() + timezone.timedelta(days=faker.pyint()))

    slug_url = factory.Sequence(lambda n: f'{n}{faker.slug()}')

    repository = factory.LazyAttribute(lambda _: faker.url())
    video_channel = factory.LazyAttribute(lambda _: faker.url())
    facebook_group = factory.LazyAttribute(lambda _: faker.url())

    class Meta:
        model = Course

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        new_kwargs = deepcopy(kwargs)
        if not kwargs.get('end_date'):
            end_date = kwargs.get('start_date') + timezone.timedelta(days=faker.pyint())
            new_kwargs['end_date'] = end_date
        return create_course(*args, **new_kwargs)


class WeekFactory(factory.DjangoModelFactory):
    number = factory.LazyAttribute(lambda _: faker.pyint())

    start_date = factory.LazyAttribute(lambda _: faker.date_object())
    end_date = factory.LazyAttribute(lambda _: faker.date_object())

    course = factory.SubFactory(CourseFactory)

    class Meta:
        model = Week


class MaterialFactory(factory.DjangoModelFactory):
    identifier = factory.Sequence(lambda n: f'{n}{faker.word()}')
    url = factory.Sequence(lambda n: f'{faker.url()}{n}')
    content = factory.LazyAttribute(lambda _: faker.text())

    class Meta:
        model = Material


class IncludedMaterialFactory(factory.DjangoModelFactory):
    material = factory.SubFactory(MaterialFactory)
    week = factory.SubFactory(WeekFactory)
    course = factory.SubFactory(CourseFactory)

    class Meta:
        model = IncludedMaterial

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        material = kwargs.get('material')
        fields = ('identifier', 'url', 'content')
        for field in fields:
            if not kwargs.get(field):
                kwargs[field] = material.__dict__.get(field)
        return IncludedMaterial.objects.create(**kwargs)


class TaskFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'{n}{faker.word()}')
    description = factory.LazyAttribute(lambda _: faker.text())
    gradable = factory.LazyAttribute(lambda _: faker.boolean())

    class Meta:
        model = Task


class IncludedTaskFactory(factory.DjangoModelFactory):
    week = factory.SubFactory(WeekFactory)
    course = factory.SubFactory(CourseFactory)
    task = factory.SubFactory(TaskFactory)

    class Meta:
        model = IncludedTask

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        fields = ('name', 'description', 'gradable')
        task = kwargs.get('task')
        for field in fields:
            if kwargs.get(field) is None:
                kwargs[field] = task.__dict__.get(field)
        return IncludedTask.objects.create(**kwargs)


class ProgrammingLanguageFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(lambda _: faker.word())
    test_format = factory.LazyAttribute(lambda _: faker.file_name())
    requirements_format = factory.LazyAttribute(lambda _: faker.file_name())

    class Meta:
        model = ProgrammingLanguage


class TaskTestFactory(factory.DjangoModelFactory):
    language = factory.SubFactory(ProgrammingLanguageFactory)

    class Meta:
        model = Test


class SourceCodeTestFactory(TaskTestFactory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs['code'] = faker.text()
        return create_test_for_task(*args, **kwargs)


class BinaryFileTestFactory(TaskTestFactory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs['file'] = SimpleUploadedFile('file.jar', bytes(f'{faker.text}'.encode('utf-8')))
        return create_test_for_task(*args, **kwargs)


class SolutionFactory(factory.DjangoModelFactory):
    task = factory.SubFactory(IncludedTaskFactory)
    user = factory.SubFactory(BaseUserFactory)
    url = factory.LazyAttribute(lambda _: faker.url())
    code = factory.LazyAttribute(lambda _: faker.text())
    build_id = factory.LazyAttribute(lambda _: faker.pyint())
    test_output = factory.LazyAttribute(lambda _: faker.text())

    class Meta:
        model = Solution
