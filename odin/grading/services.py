from django.db import transaction


def start_grader_communication(*,
                               solution_id: int,
                               solution_model: str
                               ):

    from odin.grading.tasks import submit_solution

    transaction.on_commit(lambda: submit_solution.delay(solution_id, solution_model))
