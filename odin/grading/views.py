from rest_framework.views import APIView

from django.conf import settings
from django.shortcuts import get_object_or_404

from .services import create_plain_problem, create_binary_problem
from .serializers import GraderBinaryProblemSerializer, GraderPlainProblemSerializer
from .client import DjangoGraderClient


class SolutionsAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        solution_id = data.get('solution_id')
        solution_model = settings.GRADER_SOLUTION_MODEL

        solution = get_object_or_404(solution_model, id=solution_id)
        if solution.code:
            file_type = 'plain'
        if solution.file:
            file_type = 'binary'
        test = solution.task.test
        data = {
            'language': test.language,
            'test_type': test.test_type,
            'file_type': file_type,
            'test': test,
            'extra_options': test.extra_options
        }

        if test.is_source():
            data['code'] = solution.code
            problem = create_plain_problem(**data)
            grader_ready_data = GraderPlainProblemSerializer(problem)
        else:
            data['code'] = solution.file
            problem = create_binary_problem(**data)
            grader_ready_data = GraderBinaryProblemSerializer(problem)

        client = DjangoGraderClient(solution_model, settings, grader_ready_data)
        client.submit_solution(solution)
        return super().post(request, *args, **kwargs)
