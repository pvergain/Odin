from test_plus import TestCase
from odin.education.apis.permissions import (
    IsStudentPermission,
    IsTeacherPermission,
    IsStudentOrTeacherInCoursePermission,
    IsStudentOrTeacherPermission,
)

from odin.users.factories import BaseUserFactory
from odin.education.models import Student, Teacher, CourseAssignment
from odin.education.factories import CourseFactory
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

        self.assertFalse(self.user.is_teacher())
        self.assertTrue(permissions.has_permission(self.request, None))

    def test_permission_if_user_is_not_student(self):
        permissions = IsStudentPermission()

        self.assertFalse(self.user.is_student())
        self.assertFalse(permissions.has_permission(self.request, None))


class TestIsTeacherPermission(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()
        self.request = Mock()
        self.request.user = self.user

    def test_permission_if_user_is_not_teacher(self):
        permission = IsTeacherPermission()

        self.assertFalse(self.user.is_teacher())
        self.assertFalse(permission.has_permission(self.request, None))

    def test_permission_if_user_is_teacher(self):
        permission = IsTeacherPermission()

        teacher = Teacher.objects.create_from_user(self.user)
        teacher.save()

        self.assertTrue(permission.has_permission(self.request, None))


class TestIsStudentOrTeacherPermission(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()
        self.user.is_active = True
        self.user.save()
        self.request = Mock()
        self.request.user = self.user

    def test_permission_if_user_is_not_student_or_teacher(self):
        permissions = IsStudentOrTeacherPermission()

        self.assertFalse(self.user.is_student())
        self.assertFalse(self.user.is_teacher())
        self.assertFalse(permissions.has_permission(self.request, None))

    def test_permission_if_user_is_student(self):
        student = Student.objects.create_from_user(self.user)
        student.save()

        permissions = IsStudentOrTeacherPermission()

        self.assertTrue(self.user.is_student())
        self.assertFalse(self.user.is_teacher())
        self.assertTrue(permissions.has_permission(self.request, None))

    def test_permission_if_user_is_teacher(self):
        teacher = Teacher.objects.create_from_user(self.user)
        teacher.save()

        permissions = IsStudentOrTeacherPermission()

        self.assertTrue(self.user.is_teacher())
        self.assertFalse(self.user.is_student())
        self.assertTrue(permissions.has_permission(self.request, None))

    def test_permission_if_user_is_teacher_and_student(self):
        teacher = Teacher.objects.create_from_user(self.user)
        teacher.save()

        student = Student.objects.create_from_user(self.user)
        student.save()

        permissions = IsStudentOrTeacherPermission()

        self.assertTrue(self.user.is_student())
        self.assertTrue(self.user.is_teacher())
        self.assertTrue(permissions.has_permission(self.request, None))


class TestIsStudentOrTeacherInCoursePermission(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()
        self.user.is_active = True
        self.user.save()
        self.request = Mock()
        self.request.user = self.user
        self.course = CourseFactory()
        self.view = make_mock_object()
        self.view.kwargs = {'course_id': self.course.id}

    def test_permission_if_user_is_not_student_or_teacher_in_course(self):

        permissions = IsStudentOrTeacherInCoursePermission()

        self.assertFalse(permissions.has_permission(self.request, self.view))

    def test_permission_if_user_is_student_in_course(self):
        student = Student.objects.create_from_user(self.user)
        student.save()

        ca = CourseAssignment()

        ca.course = self.course
        ca.student = student
        ca.save()

        permissions = IsStudentOrTeacherInCoursePermission()

        self.assertTrue(self.user.is_student())
        self.assertTrue(permissions.has_permission(self.request, self.view))

    def test_permission_if_user_is_teacher_in_course(self):
        teacher = Teacher.objects.create_from_user(self.user)
        teacher.save()

        ca = CourseAssignment()

        ca.course = self.course
        ca.teacher = teacher
        ca.save()

        permissions = IsStudentOrTeacherInCoursePermission()

        self.assertTrue(self.user.is_teacher())
        self.assertTrue(permissions.has_permission(self.request, self.view))

    def test_permission_if_user_is_student_and_teacher_in_course(self):
        teacher = Teacher.objects.create_from_user(self.user)
        teacher.save()

        student = Student.objects.create_from_user(self.user)
        student.save()

        ca1 = CourseAssignment()
        ca2 = CourseAssignment()

        ca1.course = self.course
        ca1.teacher = teacher
        ca1.save()

        ca2.course = self.course
        ca2.student = student
        ca2.save()

        permissions = IsStudentOrTeacherInCoursePermission()

        self.assertTrue(self.user.is_teacher())
        self.assertTrue(self.user.is_student())
        self.assertTrue(permissions.has_permission(self.request, self.view))
