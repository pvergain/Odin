from datetime import datetime, timedelta

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


def create_course(*,
                  name: str,
                  start_date: datetime,
                  end_date: datetime,
                  repository: str,
                  facebook_group: str,
                  video_channel: str,
                  slug_url: str=None):

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

    for i in range(1, weeks + 1):
        Week.objects.create(course=course,
                            number=i,
                            start_date=start_date,
                            end_date=start_date + timedelta(days=7))
        start_date = start_date + timedelta(days=7)

    return course


def create_topic(*,
                 name: str,
                 week: Week,
                 course: Course):
    if Topic.objects.filter(course=course, name=name).exists():
        raise ValidationError('Topic with this name already exists for this course')

    topic = Topic.objects.create(name=name, course=course, week=week)

    return topic


# TODO check what to validate here
def create_included_material(*,
                             identifier: str,
                             url: str,
                             topic: Topic):
    material = Material.objects.create(identifier=identifier, url=url)
    included_material = IncludedMaterial.objects.create(material=material, topic=topic)

    return included_material
