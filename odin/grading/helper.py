from .serializers import GraderPlainProblemSerializer, GraderBinaryProblemSerializer
from . import services


def get_grader_ready_data(solution_id, solution_model):
    solution = solution_model.objects.get(id=solution_id)
    test = solution.task.test
    if solution.code:
        file_type = 'plain'
        test_resource = test.sourcecodetest.code
    if solution.file:
        file_type = 'binary'
        test_resource = test.binaryfiletest.file
    data = {
        'language': test.language.name,
        'test_type': 'unittest',
        'file_type': file_type,
        'test': test_resource,
        'extra_options': test.extra_options
    }

    if test.is_source():
        data['code'] = solution.code
        problem = services.create_plain_problem(**data)
        grader_ready_data = GraderPlainProblemSerializer(problem).data
    else:
        data['code'] = solution.file
        problem = services.create_binary_problem(**data)
        grader_ready_data = GraderBinaryProblemSerializer(problem).data

    return grader_ready_data
