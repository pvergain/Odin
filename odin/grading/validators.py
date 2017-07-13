from django.core.exceptions import ValidationError


GRADER_SUPPORTED_LANGUAGES = [
    'python',
    'ruby',
    'java',
    'javascript'
]

GRADER_SUPPORTED_FILE_TYPES = [
    'plain',
    'binary'
]


def create_problem_service_validation(*,
                                      language: str="",
                                      test_type: str="unittest",
                                      file_type: str="plain") -> bool:

    if language not in GRADER_SUPPORTED_LANGUAGES:
        raise ValidationError("Programming language not supported")

    if test_type != 'unittest':
        raise ValidationError('Test type not supported')

    if file_type not in GRADER_SUPPORTED_FILE_TYPES:
        raise ValidationError("File type is not supported")

    return True
