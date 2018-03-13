from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.permissions import BasePermission

from odin.authentication.apis.permissions import JSONWebTokenAuthenticationMixin

from odin.education.models import Course, Student


class StudentCoursesApi(JSONWebTokenAuthenticationMixin, ListAPIView):
    class IsStudentPermission(BasePermission):
        def has_permission(self, request, view):
            user = request.user
            student = user.downcast(Student)

            if student is not None:
                view.student = student
                return True

            return False

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = Course
            fields = ('id',
                      'name',
                      'start_date',
                      'end_date',
                      'logo',
                      'slug_url')

    serializer_class = Serializer

    def get_permissions(self):
        return super().get_permissions() + [self.IsStudentPermission()]

    def get_queryset(self):
        return Course.objects\
                     .filter(course_assignments__student=self.student)\
                     .order_by('-id')
