from django.core.exceptions import ValidationError

GRADER_SUPPORTED_LANGUAGES = [
    'python',
    'ruby',
    'java',
    'javascript'
]

GRADER_SUPPORTED_TEST_TYPES = {
    'UNITTEST': 'unittest',
    'OUTPUT_CHECKING': 'output_checking'
}

GRADER_SUPPORTED_FILE_TYPES = {
    'BINARY': 'binary',
    'PLAIN': 'plain'
}


def run_create_grader_ready_data_validation(
    *,
    language: str,
    test_type: str,
    file_type: str
):

    if language not in GRADER_SUPPORTED_LANGUAGES:
        raise ValidationError("Programming language not supported")

    if test_type not in GRADER_SUPPORTED_TEST_TYPES:
        raise ValidationError('Test type not supported')

    if file_type not in GRADER_SUPPORTED_FILE_TYPES:
        raise ValidationError("File type is not supported")
