from rest_framework import serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView

from odin.education.models import Course
from odin.education.services import get_gradable_tasks_for_course

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


class CourseDetailApi(RetrieveAPIView):
    class CourseSerializer(serializers.ModelSerializer):
        problems = serializers.SerializerMethodField()

        class Meta:
            model = Course
            fields = ('id',
                      'name',
                      'start_date',
                      'end_date',
                      'logo',
                      'slug_url',
                      'problems')

        def get_problems(self, obj):
            tasks = get_gradable_tasks_for_course(course=obj)

            return [
                {
                    'name': task.name,
                    'description': task.description,
                    'gradable': task.gradable
                } for task in tasks
            ]

    serializer_class = CourseSerializer
    lookup_url_kwarg = 'course_id'

    def get_queryset(self):
        return Course.objects.prefetch_related('topics__tasks')
