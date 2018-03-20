from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response

from odin.apis.mixins import ServiceExceptionHandlerMixin

from odin.education.models import Solution

from odin.education.apis.permissions import StudentCourseAuthenticationMixin

from odin.education.services import create_gradable_solution

from odin.education.apis.serializers import SolutionSubmitSerializer

from odin.grading.services import start_grader_communication


class SolutionSubmitApi(StudentCourseAuthenticationMixin, ServiceExceptionHandlerMixin, APIView):
    def get(self, request, *args, **kwargs):
        solution_id = kwargs['solution_id']
        solution = get_object_or_404(Solution, id=solution_id)
        if solution:
            solution = {
                'solution_id': solution.id,
                'solution_status': solution.verbose_status,
                'code': solution.code,
                'test_result': solution.test_output
            }
            return Response(solution)

    def post(self, request):
        serializer = SolutionSubmitSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        create_gradable_solution_kwargs = {
            'student': self.request.user.student,
            'task': serializer.validated_data['task'],
            'code': serializer.validated_data['code']
        }

        solution = create_gradable_solution(**create_gradable_solution_kwargs)
        if solution:
            start_grader_communication(solution.id, 'education.Solution')
            solution = {
                'solution_id': solution.id,
                'solution_status': solution.verbose_status,
                'code': solution.code,
                'test_result': solution.test_output
            }

            return Response(solution)
        else:
            return Response({'problem': 'error occured'})
