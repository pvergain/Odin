from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response

from odin.apis.mixins import ServiceExceptionHandlerMixin

from odin.education.models import Solution

from odin.education.apis.permissions import CourseAuthenticationMixin

from odin.education.services import create_solution

from odin.education.apis.serializers import SolutionSubmitSerializer


class SolutionSubmitApi(
    ServiceExceptionHandlerMixin,
    CourseAuthenticationMixin,
    APIView
):

    def get(self, request, *args, **kwargs):
        solution = get_object_or_404(Solution, id=self.kwargs.get('solution_id'))
        data = {
            'solution_id': solution.id,
            'solution_status': solution.verbose_status,
            'code': solution.code,
            'test_result': solution.test_output
        }
        return Response(data)

    def post(self, request):
        serializer = SolutionSubmitSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        solution = create_solution(
            user=self.request.user,
            task=serializer.validated_data['task'],
            code=serializer.validated_data.get('code'),
            url=serializer.validated_data.get('url')
        )

        data = {
                'solution_id': solution.id,
                'solution_status': solution.verbose_status,
                'code': solution.code,
                'url': solution.url,
                'test_result': solution.test_output
            }

        return Response(data)
