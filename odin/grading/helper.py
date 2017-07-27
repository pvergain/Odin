from typing import Dict

from django.db.models import Model

from .models import GraderBinaryProblem, GraderPlainProblem
from .serializers import GraderPlainProblemSerializer, GraderBinaryProblemSerializer
from . import services


def get_grader_ready_data(solution_id: int, solution_model: Model) -> Dict:
    solution = solution_model.objects.get(id=solution_id)
    test = solution.task.test

    if solution.code:
        file_type = GraderPlainProblem.PLAIN
        test_resource = test.code

    if solution.file:
        file_type = GraderBinaryProblem.BINARY
        test_resource = test.file

    if test.extra_options is None:
        test.extra_options = {}

    data = {
        'language': test.language.name,
        'test_type': GraderPlainProblem.UNITTEST,
        'file_type': file_type,
        'test': test_resource,
        'extra_options': test.extra_options
    }

    if test.is_source():
        data['solution'] = solution.code
        problem = services.create_plain_problem(**data)
        grader_ready_data = GraderPlainProblemSerializer(problem).data
    else:
        data['solution'] = solution.file
        problem = services.create_binary_problem(**data)
        grader_ready_data = GraderBinaryProblemSerializer(problem).data

    return grader_ready_data
