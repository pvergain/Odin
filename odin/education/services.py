from datetime import datetime, timedelta
from typing import Dict, BinaryIO

from django.db import transaction
from django.core.exceptions import ValidationError

from odin.users.models import BaseUser

from .models import (
    Course,
    CourseAssignment,
    Student,
    Teacher,
    CheckIn,
    Week,
    Topic,
    IncludedMaterial,
    Material,
    IncludedTask,
    Task,
    ProgrammingLanguage,
    Solution,
    Test,
    IncludedTest
)
from .helper import get_dates_for_weeks, percentage_presence


def add_student(course: Course, student: Student) -> CourseAssignment:
    teacher = Teacher.objects.filter(user=student.user)
    if teacher:
        course_assignment = CourseAssignment.objects.filter(course=course, teacher=teacher)
        if course_assignment:
            raise ValidationError("User is already a teacher for this course!")
    s = CourseAssignment.objects.filter(course=course, student=student)
    if s:
        raise ValidationError("User is already a student for this course!")

    return CourseAssignment.objects.create(course=course, student=student)


def add_teacher(course: Course, teacher: Teacher, hidden: bool=False) -> CourseAssignment:
    student = Student.objects.filter(user=teacher.user)
    if student:
        course_assignment = CourseAssignment.objects.filter(course=course, student=student)
        if course_assignment:
            raise ValidationError("User is already a student for this course!")
    t = CourseAssignment.objects.filter(course=course, teacher=teacher)
    if t:
        raise ValidationError("User is already a student for this course!")

    return CourseAssignment.objects.create(course=course, teacher=teacher, hidden=hidden)


@transaction.atomic
def create_course(*,
                  name: str,
                  start_date: datetime,
                  end_date: datetime,
                  repository: str,
                  facebook_group: str=None,
                  video_channel: str=None,
                  slug_url: str=None,
                  public: bool=True) -> Course:

    if Course.objects.filter(name=name).exists():
        raise ValidationError('Course already exists')

    course = Course.objects.create(
        name=name,
        start_date=start_date,
        end_date=end_date,
        repository=repository,
        facebook_group=facebook_group,
        video_channel=video_channel,
        slug_url=slug_url,
        public=public
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

    included_material.identifier = existing_material.identifier
    included_material.url = existing_material.url
    included_material.content = existing_material.content

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

    included_task.name = existing_task.name
    included_task.description = existing_task.description
    included_task.gradable = existing_task.gradable

    included_task.task = existing_task
    included_task.full_clean()
    included_task.save()

    return included_task


def create_test_for_task(*,
                         existing_test: Test=None,
                         task: IncludedTask,
                         language: ProgrammingLanguage,
                         extra_options: Dict={},
                         code: str=None,
                         file: BinaryIO=None):

    new_test = IncludedTest(task=task)
    if existing_test is None:
        existing_test = Test(language=language, extra_options=extra_options, code=code, file=file)
        existing_test.full_clean()
        existing_test.save()

    new_test.language = existing_test.language
    new_test.extra_options = existing_test.extra_options
    new_test.code = existing_test.code
    new_test.file = existing_test.file

    new_test.test = existing_test
    new_test.save()

    return new_test


def create_gradable_solution(*,
                             task: IncludedTask,
                             student: Student,
                             code: str=None,
                             file: BinaryIO=None) -> Solution:
    if code is not None and file is not None:
        raise ValidationError("Provide either code or a file, not both!")
    if code is None and file is None:
        raise ValidationError("Provide either code or a file!")
    if code is not None:
        new_solution = Solution.objects.create(
            task=task,
            student=student,
            code=code,
            status=6
        )
    if file is not None:
        new_solution = Solution.objects.create(
            task=task,
            student=student,
            file=file,
            status=6
        )

    return new_solution


def create_non_gradable_solution(*,
                                 task: IncludedTask,
                                 student: Student,
                                 url: str=None) -> Solution:
    if url is None:
            raise ValidationError("Provide a url!")
    new_solution = Solution.objects.create(
        task=task,
        student=student,
        url=url,
        status=6
    )

    return new_solution


def get_presence_for_course(*,
                            course: Course,
                            user: BaseUser) -> dict:
    presence_for_course = {}
    if course.lectures.exists():
        lecture_dates_for_weeks = get_dates_for_weeks(course)
        user_dates = CheckIn.objects.get_user_dates(user, course)

        presence_for_course = {
            'weeks': list(lecture_dates_for_weeks.keys()),
            'lecture_dates_for_weeks': lecture_dates_for_weeks,
            'user_dates': user_dates,
            'percentage_presence': percentage_presence(user_dates, course)
        }

        return presence_for_course
