import base64
import tempfile
import os
import tarfile

from typing import Dict, List

from django.db.models import Model
from django.core.exceptions import ValidationError

from .validators import run_create_grader_ready_data_validation

from odin.education.models import IncludedTest


TEST_TYPES = {
    'UNITTEST': 'unittest',
    'OUTPUT_CHECKING': 'output_checking'
}

FILE_TYPES = {
    'BINARY': 'binary',
    'PLAIN': 'plain'
}


def encode_solution_or_test_code(code: str):
    if isinstance(code, bytes):
        return base64.b64encode(code).decode('ascii')
    return base64.b64encode(code.encode('UTF-8')).decode('ascii')


def generate_test_file(*, test: IncludedTest, path: str, ):
    with open(f'{path}/{test.language.test_format}', 'w', encoding='UTF-8') as testfile:
            testfile.write(test.code)


def generate_dependency_file(*, test: IncludedTest, path: str):
    with open(f'{path}/{test.language.requirements_format}', 'w', encoding='UTF-8') as requirements:
            requirements.write(test.requirements)


def generate_tar_file_for_tests(*, test_files: List[str], path: str):
    with tarfile.open(name=f'{path}/tests.tar.gz', mode='w:gz') as tar:
            for file in test_files:
                tar.add(f'{path}/{file}', arcname=file)

    return tar.name


def encode_tests_archive(*, tar_filename: str):
    with open(tar_filename, 'rb') as tar_binary:
            encoded_archive = base64.b64encode(tar_binary.read())

    return encoded_archive


def generate_test_resource(*, test: IncludedTest):

    with tempfile.TemporaryDirectory() as tmpdir:
        generate_test_file(test=test, path=tmpdir)

        generate_dependency_file(test=test, path=tmpdir)

        test_files = os.listdir(tmpdir)

        encoded = encode_tests_archive(
            tar_filename=generate_tar_file_for_tests(test_files=test_files, path=tmpdir)
        )

    return encoded.decode('ascii')


def get_grader_ready_data(solution_id: int, solution_model: Model) -> Dict:
    solution = solution_model.objects.get(id=solution_id)
    test = solution.task.test

    file_type = FILE_TYPES['BINARY']
    test_type = TEST_TYPES['UNITTEST']

    if test.extra_options is None:
        test.extra_options = {}

    if solution.code:

        solution_code = encode_solution_or_test_code(code=solution.code)

        if not test.requirements:
            test_resource = encode_solution_or_test_code(code=test.code)
        else:
            test_resource = generate_test_resource(test=test)

            test.extra_options['archive_test_type'] = True
            test.extra_options['time_limit'] = 20

    if solution.file:
        solution_code = encode_solution_or_test_code(code=solution.file.read())
        if test.file:
            test_resource = encode_solution_or_test_code(code=test.file.read())
        elif not test.requirements:
            test_resource = encode_solution_or_test_code(code=test.code)
        else:
            test_resource = generate_test_resource(test=test)

        test.extra_options['archive_test_type'] = True
        test.extra_options['time_limit'] = 20
        test.extra_options['archive_solution_type'] = True

    data = {
        'language': test.language.name,
        'test_type': test_type,
        'solution': solution_code,
        'file_type': file_type,
        'test': test_resource,
        'extra_options': test.extra_options
    }

    if test.extra_options['archive_solution_type'] and not test.language.name == 'python':
        raise ValidationError('Cannot submit archived solution if language is not python')

    if not test.is_source():
        data['test_type'] = TEST_TYPES['OUTPUT_CHECKING']

    run_create_grader_ready_data_validation(
        language=test.language.name,
        test_type=data['test_type'],
        file_type=data['file_type']
    )

    return data
