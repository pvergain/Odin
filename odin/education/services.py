from datetime import datetime, timedelta

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
    Material
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
                  facebook_group: str,
                  video_channel: str,
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
                             material: Material=None) -> IncludedMaterial:

    included_material = IncludedMaterial(topic=topic)

    if material is None:
        if Material.objects.filter(identifier=identifier).exists():
            raise ValidationError("Material already exists")
        material = Material.objects.create(identifier=identifier, url=url, content=content)
    else:
        if IncludedMaterial.objects.filter(identifier=material.identifier).exists():
            raise ValidationError("Material already exists")
    included_material.__dict__.update(material.__dict__)

    included_material.material = material
    included_material.save()

    return included_material
