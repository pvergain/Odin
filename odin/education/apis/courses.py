from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response

from odin.education.models import (
    Course,
    Student,
    Teacher,
    Week,
)

from odin.education.services import get_gradable_tasks_for_course

from .permissions import (
    IsUserStudentOrTeacherMixin,
    IsStudentOrTeacherInCourseMixin,
)


class StudentCoursesApi(IsUserStudentOrTeacherMixin, ListAPIView):
    class Serializer(serializers.ModelSerializer):
        students_count = serializers.SerializerMethodField()
        description = serializers.CharField(source='description.verbose')

        class Meta:
            model = Course
            fields = ('id',
                      'name',
                      'start_date',
                      'end_date',
                      'logo',
                      'slug_url',
                      'description',
                      'students_count')

        def get_students_count(self, obj):
            return obj.students.filter(is_active=True).count()

    serializer_class = Serializer

    def get_queryset(self):
        user = self.request.user

        student = user.downcast(Student)
        teacher = user.downcast(Teacher)

        if teacher:
            return Course.objects\
                .filter(teachers__in=[teacher])\
                .order_by('-id')

        return Course.objects\
                     .filter(course_assignments__student=student)\
                     .order_by('-id')


class CourseDetailApi(IsStudentOrTeacherInCourseMixin, APIView):
    class CourseSerializer(serializers.ModelSerializer):
        class WeekSerializer(serializers.ModelSerializer):
            class Meta:
                model = Week
                fields = ('number',)

        problems = serializers.SerializerMethodField()
        weeks = WeekSerializer(many=True)

        class Meta:
            model = Course
            fields = ('id',
                      'name',
                      'start_date',
                      'end_date',
                      'logo',
                      'slug_url',
                      'weeks',
                      'problems')

        def get_problems(self, obj):
            return [
                {
                    'id': task.id,
                    'name': task.name,
                    'description': task.description,
                    'gradable': task.gradable,
                    'week': task.week.number,
                    'last_solution': task.last_solution and {
                        'id': task.last_solution.id,
                        'status': task.last_solution.verbose_status,
                        'code': task.last_solution.code
                    } or None
                } for task in obj.tasks
            ]

    def get_queryset(self):
        return Course.objects.prefetch_related('weeks__tasks')

    def get(self, request, course_id):
        course = get_object_or_404(self.get_queryset(), pk=course_id)
        student = self.request.user.downcast(Student)

        course.tasks = get_gradable_tasks_for_course(course=course, student=student)

        return Response(self.CourseSerializer(instance=course).data)
