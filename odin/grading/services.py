from typing import Dict, BinaryIO

from .models import GraderBinaryProblem, GraderPlainProblem


def create_plain_problem(*,
                         language: str="",
                         test_type: str="unittest",
                         file_type: str="plain",
                         code: str=None,
                         test: str=None,
                         extra_options: Dict={}) -> GraderPlainProblem:
    return GraderPlainProblem.objects.create(
        language=language,
        test_type=test_type,
        file_type=file_type,
        code=code,
        test=test,
        extra_options=extra_options
    )


def create_binary_problem(*,
                          language: str="",
                          test_type: str="unittest",
                          file_type: str="binary",
                          code: BinaryIO=None,
                          test: BinaryIO=None,
                          extra_options: Dict={}) -> GraderBinaryProblem:
    return GraderBinaryProblem.objects.create(
        language=language,
        test_type=test_type,
        file_type=file_type,
        code=code,
        test=test,
        extra_options=extra_options
    )
