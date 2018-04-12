from odin.education.models import IncludedTask

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from .permissions import CourseAuthenticationMixin

from odin.apis.mixins import ServiceExceptionHandlerMixin


class TaskDetailApi(
    ServiceExceptionHandlerMixin,
    CourseAuthenticationMixin,
    APIView
):

    class TaskSerializer(serializers.ModelSerializer):
        solutions = serializers.SerializerMethodField()
        course = serializers.SerializerMethodField()

        class Meta:
            model = IncludedTask
            fields = (
                'id',
                'name',
                'created_at',
                'description',
                'gradable',
                'course',
                'solutions'
            )

        def get_course(self, obj):
            return {
                     'id': obj.course.id,
                     'name': obj.course.name
                   }

        def get_solutions(self, obj):
            solutions = [
                {
                    'id': solution.id,
                    'code': solution.code,
                    'status': solution.verbose_status,
                    'test_result': solution.test_output,
                    'student_id': solution.user_id
                } for solution in obj.valid_solutions
            ]

            if solutions:
                return solutions
            else:
                return []

    def get(self, request, task_id):
        user = self.request.user
        task = IncludedTask.objects.get(id=task_id)

        task.valid_solutions = task.solutions.filter(user_id=user.id).order_by('-id')

        return Response(self.TaskSerializer(instance=task).data)
