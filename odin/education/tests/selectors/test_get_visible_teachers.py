from django.test import TestCase

from odin.education.selectors import get_visible_teachers
from odin.education.factories import (
    CourseFactory,
    TeacherFactory,
    TeacherCourseAssignmentFactory
)


class GetVisibleTeachersTests(TestCase):
    def test_selector_for_visible_teachers(self):
        course = CourseFactory()
        teacher = TeacherFactory()

        TeacherCourseAssignmentFactory(
            course=course,
            teacher=teacher,
            hidden=False
        )

        self.assertEqual([teacher], list(get_visible_teachers(course=course)))

    def test_selector_for_hidden_teachers(self):
        course = CourseFactory()
        teacher = TeacherFactory()

        TeacherCourseAssignmentFactory(
            course=course,
            teacher=teacher,
            hidden=True
        )

        self.assertEqual([], list(get_visible_teachers(course=course)))
