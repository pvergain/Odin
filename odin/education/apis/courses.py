from django.db.models import Q

from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response

from odin.apis.mixins import ServiceExceptionHandlerMixin

from odin.education.models import (
    Course,
    Student,
    Teacher,
    Week,
    ProgrammingLanguage,
)

from odin.education.services import (
    create_included_task_with_test,
    get_gradable_tasks_for_course
)

from odin.education.apis.permissions import (
    CourseAuthenticationMixin,
    TeacherCourseAuthenticationMixin,
    CourseDetailAuthenticationMixin,
)


class StudentCoursesApi(
    CourseAuthenticationMixin,
    ServiceExceptionHandlerMixin,
    ListAPIView
):

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

        teacher = user.downcast(Teacher)
        student = user.downcast(Student)

        return Course.objects.filter(
            Q(teachers__in=[teacher]) | Q(students__in=[student])
        ).distinct()


class CourseDetailApi(
    ServiceExceptionHandlerMixin,
    CourseDetailAuthenticationMixin,
    CourseAuthenticationMixin,
    APIView
):

    class CourseSerializer(serializers.ModelSerializer):
        problems = serializers.SerializerMethodField()
        languages = serializers.SerializerMethodField()
        weeks = serializers.SerializerMethodField()

        class Meta:
            model = Course
            fields = (
                'id',
                'name',
                'start_date',
                'end_date',
                'logo',
                'slug_url',
                'problems',
                'weeks',
                'languages'
            )

        def get_problems(self, obj):
            return [
                {
                    'id': task.id,
                    'name': task.name,
                    'gradable': task.gradable,
                    'week': {
                        'id': task.week.id,
                        'number': task.week.number
                    },
                    'description': task.description,
                    'last_solution': task.last_solution and {
                        'id': task.last_solution.id,
                        'status': task.last_solution.verbose_status,
                        'code': task.last_solution.code
                    } or None
                } for task in obj.tasks
            ]

        def get_languages(self, obj):
            return [
                {
                    'id': language.id,
                    'name': language.name,
                } for language in ProgrammingLanguage.objects.all()
            ]

        def get_weeks(self, obj):
            return [
                {
                    'id': week.id,
                    'number': week.number,
                } for week in obj.weeks.all()
            ]

    def get_queryset(self):
        return Course.objects.prefetch_related('weeks__included_tasks')

    def get(self, request, course_id):
        course = get_object_or_404(self.get_queryset(), pk=course_id)
        student = self.request.user.downcast(Student)

        course.tasks = get_gradable_tasks_for_course(course=course, student=student)

        return Response(self.CourseSerializer(instance=course).data)


class TeacherCourseDetailApi(TeacherCourseAuthenticationMixin, APIView):
    # Pending deprecation, rebase FE functionality to CourseDetailApi only
    class Serializer(serializers.ModelSerializer):

        weeks = serializers.SerializerMethodField()
        languages = serializers.SerializerMethodField()

        class Meta:
            model = Course
            fields = (
                'id',
                'name',
                'start_date',
                'end_date',
                'logo',
                'slug_url',
                'languages',
                'weeks',
            )

        def get_weeks(self, obj):
            return [
                {
                    'id': week.id,
                    'number': week.number,
                    'tasks': [
                        {
                            'id': task.id,
                            'name': task.name,
                            'gradable': task.gradable,
                            'description': task.description,
                        } for task in week.included_tasks.all()
                    ]
                } for week in obj.weeks.all()
            ]

        def get_languages(self, obj):
            return [
                {
                    'id': language.id,
                    'name': language.name,
                } for language in ProgrammingLanguage.objects.all()
            ]

    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        return Response(self.Serializer(instance=course).data)


class CreateTaskApi(
    ServiceExceptionHandlerMixin,
    TeacherCourseAuthenticationMixin,
    APIView
):

    class Serializer(serializers.Serializer):
        course = serializers.PrimaryKeyRelatedField(
            queryset=Course.objects.all(),
            error_messages={
                'does_not_exist':
                ('Course does not exist')
            }
        )
        name = serializers.CharField()
        code = serializers.CharField()
        requirements = serializers.CharField(required=False)
        description_url = serializers.URLField()
        gradable = serializers.BooleanField()
        language = serializers.PrimaryKeyRelatedField(
            queryset=ProgrammingLanguage.objects.all(),
            error_messages={
                'does_not_exists':
                ('Programming Language does not exist')
            }
        )
        week = serializers.PrimaryKeyRelatedField(
            queryset=Week.objects.all(),
            error_messages={
                'does_not_exist':
                ('Week does not exist')
            }
        )

    def post(self, request, course_id):
        data = request.data
        data['course'] = course_id
        serializer = self.Serializer(data=data)
        serializer.is_valid(raise_exception=True)

        task = create_included_task_with_test(**serializer.validated_data)

        data = {
            'task_id': task.id,
            'task_name': task.name,
            'gradable': task.gradable,
        }

        return Response(data=data, status=status.HTTP_201_CREATED)
