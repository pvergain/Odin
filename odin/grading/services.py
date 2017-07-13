from typing import Dict, BinaryIO

from .models import GraderBinaryProblem, GraderPlainProblem
<<<<<<< 01551c1857102ee984c6596c9db8c8247e218994
<<<<<<< 23d2ac7b12094bdeef9042988b6f53a1e88164c4
from .validators import create_problem_service_validation
from .tasks import submit_solution
=======
>>>>>>> Add grader serializers and models
=======
from .validators import create_problem_service_validation
>>>>>>> Add validation for grading services + tests


def create_plain_problem(*,
                         language: str="",
                         test_type: str="unittest",
                         file_type: str="plain",
                         code: str=None,
                         test: str=None,
                         extra_options: Dict={}) -> GraderPlainProblem:
<<<<<<< 01551c1857102ee984c6596c9db8c8247e218994
<<<<<<< 23d2ac7b12094bdeef9042988b6f53a1e88164c4
=======
>>>>>>> Add validation for grading services + tests
    if create_problem_service_validation(language=language,
                                         test_type=test_type,
                                         file_type=file_type):
        return GraderPlainProblem.objects.create(
            language=language,
            test_type=test_type,
            file_type=file_type,
            code=code,
            test=test,
            extra_options=extra_options
        )
<<<<<<< 01551c1857102ee984c6596c9db8c8247e218994
=======
    return GraderPlainProblem.objects.create(
        language=language,
        test_type=test_type,
        file_type=file_type,
        code=code,
        test=test,
        extra_options=extra_options
    )
>>>>>>> Add grader serializers and models
=======
>>>>>>> Add validation for grading services + tests


def create_binary_problem(*,
                          language: str="",
                          test_type: str="unittest",
                          file_type: str="binary",
                          code: BinaryIO=None,
                          test: BinaryIO=None,
                          extra_options: Dict={}) -> GraderBinaryProblem:
<<<<<<< 01551c1857102ee984c6596c9db8c8247e218994
<<<<<<< 23d2ac7b12094bdeef9042988b6f53a1e88164c4
=======
>>>>>>> Add validation for grading services + tests
    if create_problem_service_validation(language=language,
                                         test_type=test_type,
                                         file_type=file_type):
        return GraderBinaryProblem.objects.create(
            language=language,
            test_type=test_type,
            file_type=file_type,
            code=code,
            test=test,
            extra_options=extra_options
        )
<<<<<<< 01551c1857102ee984c6596c9db8c8247e218994


def start_grader_communication(solution_id):
    submit_solution.delay(solution_id)
=======
    return GraderBinaryProblem.objects.create(
        language=language,
        test_type=test_type,
        file_type=file_type,
        code=code,
        test=test,
        extra_options=extra_options
    )
>>>>>>> Add grader serializers and models
=======
>>>>>>> Add validation for grading services + tests
