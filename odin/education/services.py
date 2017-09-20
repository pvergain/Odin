import uuid
from datetime import datetime, timedelta
from typing import Dict, BinaryIO, Tuple

from django.db import transaction
from django.core.exceptions import ValidationError

from odin.users.models import BaseUser
from odin.users.services import create_user

from .models import (
    Course,
    CourseAssignment,
    CourseDescription,
    Student,
    Teacher,
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


def add_student(course: Course, student: Student) -> CourseAssignment:
    return CourseAssignment.objects.create(course=course, student=student)


def add_teacher(course: Course, teacher: Teacher, hidden: bool=False) -> CourseAssignment:
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
                  logo: BinaryIO=None,
                  is_competition: bool=False,
                  public: bool=True,
                  description: str="") -> Course:

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
        logo=logo,
        public=public,
        is_competition=is_competition
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
    CourseDescription.objects.create(course=course, verbose=description)

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


def calculate_student_valid_solutions_for_course(*,
                                                 student: Student,
                                                 course: Course) -> str:
    total_tasks = IncludedTask.objects.filter(topic__course=course).count()
    if not total_tasks:
        return 0
    solved_tasks = Solution.objects.get_solved_solutions_for_student_and_course(student, course).count()

    ratio = (solved_tasks/total_tasks) * 100
    return f'{ratio:.1f}'


def handle_competition_registration(*,
                                    email: str,
                                    full_name: str,
                                    session_user: BaseUser) -> Tuple[bool, str]:
    """
    Handles competition registration and returns the registration token and True or
    False depending on whether further handling should be for an existing user or a
    new one.
    """
    user = BaseUser.objects.filter(email=email)
    registration_uuid = uuid.uuid4()
    if user.exists():
        user = user.first()
        user.registration_uuid = registration_uuid
        user.save()
        handle_existing_user = True
    else:
        user = create_user(email=email,
                           registration_uuid=registration_uuid,
                           profile_data={'full_name': full_name})
        handle_existing_user = False

    return (handle_existing_user, registration_uuid)


def handle_competition_login(*,
                             course: Course,
                             user: BaseUser,
                             registration_token: str) -> BaseUser:
    if not registration_token == str(user.registration_uuid):
        raise ValidationError('Token mismatch')

    if not user.is_student():
        student = Student.objects.create_from_user(user)
    else:
        student = user.student

    user.registration_uuid = None
    user.registering_for = None
    user.save()

    try:
        add_student(course=course, student=student)
    except ValidationError:
        pass

    return user


def get_all_student_solution_statistics(*,
                                        task: IncludedTask) -> Dict:
    result = {}
    course = task.topic.course
    result['total_student_count'] = course.students.count()

    filters = {'solutions__task': task, 'solutions__isnull': False}
    result['students_with_a_submitted_solution_count'] = course.students.filter(**filters).distinct().count()
    filters = {'solutions__task': task, 'solutions__status': Solution.OK}
    result['students_with_a_passing_solution_count'] = course.students.filter(**filters).distinct().count()

    return result
