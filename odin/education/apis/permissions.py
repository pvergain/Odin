from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404

from odin.authentication.permissions import JSONWebTokenAuthenticationMixin

from odin.education.models import (
    Student,
    Teacher,
)


class IsStudentPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        student = user.downcast(Student)

        if student is not None:
            return True

        return False


class IsTeacherPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        teacher = user.downcast(Teacher)

        if teacher is not None:
            return True

        return False


class IsStudentOrTeacherPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        student = user.downcast(Student)
        teacher = user.downcast(Teacher)

        if student or teacher:
            return True

        return False


class IsStudentOrTeacherInCoursePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        student = user.downcast(Student)
        teacher = user.downcast(Teacher)

        course = get_object_or_404(view.get_queryset(), pk=view.kwargs.get('course_id'))

        if (teacher and course.teachers.filter(id=teacher.id).exists())\
                or (student and course.students.filter(id=student.id).exists()):

            return True

        return False


class StudentCourseAuthenticationMixin(JSONWebTokenAuthenticationMixin):
    def get_permissions(self):
        return super().get_permissions() + [IsStudentPermission()]


class TeacherCourseAuthenticationMixin(JSONWebTokenAuthenticationMixin):
    def get_permissions(self):
        return super().get_permissions() + [IsTeacherPermission()]


class IsUserStudentOrTeacherMixin(JSONWebTokenAuthenticationMixin):
    def get_permissions(self):
        return super().get_permissions() + [IsStudentOrTeacherPermission()]


class IsStudentOrTeacherInCourseMixin(JSONWebTokenAuthenticationMixin):
    def get_permissions(self):
        return super().get_permissions() + [IsStudentOrTeacherInCoursePermission()]
