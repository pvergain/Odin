import base64
import tempfile
import os
import tarfile

from typing import Dict

from django.db.models import Model

from odin.education.models import IncludedTest

from .models import (
    GraderBinaryProblem,
    GraderPlainProblem,
    GraderPlainProblemWithRequirements
)

from .serializers import (
    GraderPlainProblemSerializer,
    GraderBinaryProblemSerializer,
    GraderPlainProblemWithRequirementsSerializer,
)

from . import services


def generate_test_resource(*, test: IncludedTest):

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f'{tmpdir}/test.py', 'w', encoding='UTF-8') as testfile:
            testfile.write(test.code)

        with open(f'{tmpdir}/requirements.txt', 'w', encoding='UTF-8') as requirements:
            requirements.write(test.requirements)

        test_files = os.listdir(tmpdir)

        with tarfile.open(name=f'{tmpdir}/tests.tar.gz', mode='w:gz') as tar:
            for file in test_files:
                tar.add(f'{tmpdir}/{file}', arcname=file)

        with open(tar.name, 'rb') as tar_b:
            encoded = base64.b64encode(tar_b.read())

    return encoded.decode('ascii')


def get_grader_ready_data(solution_id: int, solution_model: Model) -> Dict:
    solution = solution_model.objects.get(id=solution_id)
    test = solution.task.test

    if solution.code:
        if not test.requirements:
            file_type = GraderPlainProblem.PLAIN
            test_resource = test.code
        else:
            file_type = GraderPlainProblemWithRequirements.BINARY
            test_resource = generate_test_resource(test=test)

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

    if test.is_source() and not test.requirements:
        data['solution'] = solution.code
        problem = services.create_plain_problem(**data)
        grader_ready_data = GraderPlainProblemSerializer(problem).data
    elif test.is_source() and test.requirements:
        data['solution'] = solution.code
        data['test_type'] = GraderPlainProblemWithRequirements.UNITTEST
        data['extra_options'] = {'archive_test_type': True, 'time_limit': 20}
        problem = services.create_plain_problem_with_requirements(**data)
        grader_ready_data = GraderPlainProblemWithRequirementsSerializer(problem).data
    else:
        data['test_type'] = GraderBinaryProblem.OUTPUT_CHECKING
        data['solution'] = solution.file
        problem = services.create_binary_problem(**data)
        grader_ready_data = GraderBinaryProblemSerializer(problem).data

    return grader_ready_data
