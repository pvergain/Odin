from test_plus import TestCase
from odin.education.apis.permissions import (
    IsStudentPermission,
    IsTeacherPermission,
    IsStudentOrTeacherInCoursePermission,
    IsStudentOrTeacherPermission,
)

from odin.users.factories import BaseUserFactory
from odin.education.models import Student, Teacher
from unittest.mock import Mock


def make_mock_object(**kwargs):
    return type('', (object, ), kwargs)


class TestIsStudenPermission(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()
        self.request = make_mock_object(user=self.user)

    def test_permission_if_user_is_student(self):
        student = Student.objects.create_from_user(self.user)
        student.save()

        permissions = IsStudentPermission()

        self.assertTrue(permissions.has_permission(self.request, None))

    def test_permission_if_user_is_not_student(self):
        permissions = IsStudentPermission()

        self.assertFalse(permissions.has_permission(self.request, None))


class TestIsTeacherPermission(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()
        self.request = Mock()
        self.request.user = self.user

    def test_permission_if_user_is_not_teacher(self):
        permission = IsTeacherPermission()

        self.assertFalse(permission.has_permission(self.request, None))

    def test_permission_if_user_is_teacher(self):
        permission = IsTeacherPermission()

        teacher = Teacher.objects.create_from_user(self.user)
        teacher.save()

        self.assertTrue(permission.has_permission(self.request, None))


class TestIsStudentOrTeacherPermission(TestCase):
    def setUp(self):
        pass

    def test_permission_if_user_is_not_student_or_teacher(self):
        pass

    def test_permission_if_user_is_student(self):
        pass

    def test_permission_if_user_is_teacher(self):
        pass

    def test_permission_if_user_is_teacher_and_student(self):
        pass


class IsStudentOrTeacherInCoursePermission(TestCase):
    def setUp(self):
        pass

    def test_permission_if_user_is_not_student_or_teacher_in_course(self):
        pass

    def test_permission_if_user_is_student_in_course(self):
        pass

    def test_permission_if_user_is_teacher_in_course(self):
        pass

    def test_permission_if_user_is_student_and_teacher_in_course(self):
        pass
