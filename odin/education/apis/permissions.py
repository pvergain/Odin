from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404

from odin.authentication.permissions import JSONWebTokenAuthenticationMixin

from odin.education.models import (
    Student,
    Teacher,
    Course,
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
        course_id = view.kwargs['course_id']

        course = get_object_or_404(Course.objects.all(), pk=course_id)

        if teacher in course.teachers.all() or student in course.students.all():
            return True

        return False


class StudentCourseAuthenticationMixin(JSONWebTokenAuthenticationMixin):
    def get_permissions(self):
        return super().get_permissions() + [IsStudentPermission()]


class TeacherCourseAuthenticationMixin(JSONWebTokenAuthenticationMixin):
    def get_permissions(self):
        return super().get_permissions() + [IsTeacherPermission()]


class CourseAuthenticationMixin(JSONWebTokenAuthenticationMixin):
    def get_permissions(self):
        return super().get_permissions() + [IsStudentOrTeacherPermission()]


class CourseDetailAuthenticationMixin(JSONWebTokenAuthenticationMixin):
    def get_permissions(self):
        return super().get_permissions() + [IsStudentOrTeacherInCoursePermission()]
