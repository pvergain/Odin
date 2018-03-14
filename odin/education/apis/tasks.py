from odin.education.models import IncludedTask, Student
from rest_framework import serializers
from .permissions import StudentCourseAuthenticationMixin
from rest_framework.views import APIView
from rest_framework.response import Response


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
            import ipdb
            solutions = [
                {
                    'id': solution.id,
                    'code': solution.code,
                    'status': solution.verbose_status,
                    'test_result': solution.test_output,
                    'student_id': solution.student_id
                } for solution in obj.valid_solutions
            ]

            if solutions:
                return solutions
            else:
                return None

    def get(self, request, task_id):
        student = self.request.user.downcast(Student)
        task = IncludedTask.objects.get(id=task_id)
        task.valid_solutions = task.solutions.filter(student_id=student.id)

        return Response(self.TaskSerializer(instance=task).data)
