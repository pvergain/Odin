from rest_framework import serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView

from odin.education.models import Course

from .permissions import StudentCoursesAuthenticationMixin


class StudentCoursesApi(StudentCoursesAuthenticationMixin, ListAPIView):
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

    def get_queryset(self):
        return Course.objects\
                     .filter(course_assignments__student=self.student)\
                     .order_by('-id')


class CourseDetailApi(StudentCoursesAuthenticationMixin, RetrieveAPIView):
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
    queryset = Course.objects.all()
    lookup_url_kwarg = 'course_id'
