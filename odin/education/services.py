from datetime import datetime, timedelta
from typing import Dict, BinaryIO
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    Course,
    CourseAssignment,
    Student,
    Teacher,
    Week,
    Topic,
    IncludedMaterial,
    Material,
    IncludedTask,
    Task,
    ProgrammingLanguage,
    SourceCodeTest,
    BinaryFileTest,
    Test,
    Solution,
)


def add_student(course: Course, student: Student) -> CourseAssignment:
    return CourseAssignment.objects.create(course=course, student=student)


def add_teacher(course: Course, teacher: Teacher) -> CourseAssignment:
    return CourseAssignment.objects.create(course=course, teacher=teacher)


@transaction.atomic
def create_course(*,
                  name: str,
                  start_date: datetime,
                  end_date: datetime,
                  repository: str,
                  facebook_group: str=None,
                  video_channel: str=None,
                  slug_url: str=None) -> Course:

    if Course.objects.filter(name=name).exists():
        raise ValidationError('Course already exists')

    course = Course.objects.create(
        name=name,
        start_date=start_date,
        end_date=end_date,
        repository=repository,
        facebook_group=facebook_group,
        video_channel=video_channel,
        slug_url=slug_url
    )

    weeks = course.duration_in_weeks
    start_date = course.start_date
    start_date = start_date - timedelta(days=start_date.weekday())

    week_instances = []
    for i in range(1, weeks + 1):
        current = Week(course=course,
                       number=i,
                       start_date=start_date,
                       end_date=start_date + timedelta(days=7))
        start_date = current.end_date
        week_instances.append(current)

    Week.objects.bulk_create(week_instances)

    return course


def create_topic(*,
                 name: str,
                 week: Week,
                 course: Course) -> Topic:
    if Topic.objects.filter(course=course, name=name).exists():
        raise ValidationError('Topic with this name already exists for this course')

    topic = Topic.objects.create(name=name, course=course, week=week)

    return topic


def create_included_material(*,
                             identifier: str=None,
                             url: str=None,
                             topic: Topic=None,
                             content: str=None,
                             existing_material: Material=None) -> IncludedMaterial:
    included_material = IncludedMaterial(topic=topic)

    if existing_material is None:
        existing_material = Material(identifier=identifier, url=url, content=content)
        existing_material.full_clean()
        existing_material.save()

    included_material.__dict__.update(existing_material.__dict__)

    included_material.material = existing_material
    included_material.full_clean()
    included_material.save()

    return included_material


def create_included_task(*,
                         name: str=None,
                         description: str=None,
                         gradable: bool=False,
                         existing_task: Task=None,
                         topic: Topic=None) -> IncludedTask:
    included_task = IncludedTask(topic=topic)

    if existing_task is None:
        existing_task = Task(name=name, description=description, gradable=gradable)
        existing_task.full_clean()
        existing_task.save()

    included_task.__dict__.update(existing_task.__dict__)

    included_task.task = existing_task
    included_task.full_clean()
    included_task.save()

    return included_task


def create_test_for_task(*,
                         task: IncludedTask,
                         language: ProgrammingLanguage,
                         extra_options: Dict={},
                         code: str=None,
                         file: BinaryIO=None):

    base_test = Test.objects.create(task=task, language=language, extra_options=extra_options)

    if file is None and code is not None:
        new_test = SourceCodeTest(code=code)
    elif code is None and file is not None:
        new_test = BinaryFileTest(file=file)
    else:
        raise ValidationError("A binary file or source code must be provided!")

    new_test.__dict__.update(base_test.__dict__)
    new_test.full_clean()
    new_test.save()

    return new_test


def create_solution(*
                    test: Test,
                    student: Student,
                    url: str=None,
                    code: str=None,
                    file: BinaryIO=None) -> Solution:

    task_is_gradable = test.task.gradable
    if task_is_gradable:
        if code is not None and file is not None:
            raise ValidationError("Provide either code or a file, not both!")
        if code is None and file is None:
            raise ValidationError("Provide either code or a file!")
        if code is not None and file is None:
            new_solution = Solution.objects.create(
                test=test,
                student=student,
                code=code,
                status=4
            )
        if code is None and file is not None:
            new_solution = Solution.objects.create(
                test=test,
                student=student,
                file=file,
                status=4
            )
    else:
        if url is None:
            raise ValidationError("Provide a url!")
        new_solution = Solution.objects.create(
            test=test,
            student=student,
            url=url,
            status=6
        )

    return new_solution
