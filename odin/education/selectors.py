from typing import Iterable

from odin.education.models import Course, Teacher


def get_visible_teachers(*, course: Course) -> Iterable[Teacher]:
    return course.teachers.filter(course_assignments__hidden=False).select_related('profile')
