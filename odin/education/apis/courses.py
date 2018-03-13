from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response

from odin.education.models import Course, Student, IncludedTask
from odin.education.services import get_gradable_tasks_for_course

from .permissions import StudentCourseAuthenticationMixin


class StudentCoursesApi(StudentCourseAuthenticationMixin, ListAPIView):
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
        student = self.request.user.downcast(Student)

        return Course.objects\
                     .filter(course_assignments__student=student)\
                     .order_by('-id')


class CourseDetailApi(StudentCourseAuthenticationMixin, APIView):
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
            return [
                {
                    'id': task.id,
                    'name': task.name,
                    'description': task.description,
                    'gradable': task.gradable,
                    'last_solution': task.last_solution and {
                        'id': task.last_solution.id,
                        'status': task.last_solution.verbose_status,
                        'code': task.last_solution.code
                    } or None
                } for task in obj.tasks
            ]

    def get_queryset(self):
        return Course.objects.prefetch_related('topics__tasks')

    def get(self, request, course_id):
        course = get_object_or_404(self.get_queryset(), pk=course_id)
        student = self.request.user.downcast(Student)

        course.tasks = get_gradable_tasks_for_course(course=course, student=student)

        return Response(self.CourseSerializer(instance=course).data)


class TaskDetailApi(StudentCourseAuthenticationMixin, APIView):
    class TaskSerializer(serializers.ModelSerializer):
        solutions = serializers.SerializerMethodField()

        class Meta:
            model = IncludedTask
            fields = (
                'created_at',
                'description',
                'gradable',
                'solutions'
            )

        def get_solutions(self, obj):
            solutions = [
                {
                    'id': solution.id,
                    'code': solution.code,
                    'status': solution.verbose_status,
                    'test_result': solution.test_output
                } for solution in obj.solutions.all()
            ]

            if solutions:
                return solutions
            else:
                return None

    def get(self, request, task_id):
        task = IncludedTask.objects.get(id=task_id)

        return Response(self.TaskSerializer(instance=task).data)
