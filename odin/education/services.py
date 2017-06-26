from datetime import datetime, timedelta

from django.core.exceptions import ValidationError

from .models import (
    Course,
    CourseAssignment,
    Student,
    Teacher,
    Week
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
                  video_channel: str):

    if Course.objects.filter(name=name).exists():
        raise ValidationError('Course already exists')

    course = Course.objects.create(
        name=name,
        start_date=start_date,
        end_date=end_date,
        repository=repository,
        facebook_group=facebook_group,
        video_channel=video_channel
    )

    weeks = course.duration_in_weeks
    start_date = course.start_date

    for i in range(1, weeks + 1):
        Week.objects.create(course=course,
                            start_date=start_date,
                            end_date=start_date + timedelta(days=7))
        start_date = start_date + timedelta(days=7)

    return course
