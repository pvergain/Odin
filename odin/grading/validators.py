from django.core.exceptions import ValidationError

from .models import (
    GraderPlainProblem,
    GraderBinaryProblem,
    GraderPlainProblemWithRequirements,
)

GRADER_SUPPORTED_LANGUAGES = [
    'python',
    'ruby',
    'java',
    'javascript'
]

GRADER_SUPPORTED_FILE_TYPES = [
    GraderPlainProblem.PLAIN,
    GraderBinaryProblem.BINARY,
    GraderPlainProblemWithRequirements.BINARY,

]

GRADER_SUPPORTED_TEST_TYPES = [
    GraderPlainProblem.UNITTEST,
    GraderPlainProblem.OUTPUT_CHECKING,
    GraderPlainProblemWithRequirements.UNITTEST
]


def run_create_problem_service_validation(*,
                                          language: str,
                                          test_type: int,
                                          file_type: int) -> bool:

    if language not in GRADER_SUPPORTED_LANGUAGES:
        raise ValidationError("Programming language not supported")

    if test_type not in GRADER_SUPPORTED_TEST_TYPES:
        raise ValidationError('Test type not supported')

    if file_type not in GRADER_SUPPORTED_FILE_TYPES:
        raise ValidationError("File type is not supported")
