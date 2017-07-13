from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task(bind=True)
def submit_solution(grader_client, solution):
    grader_client.submit_request_to_grader(solution)


@shared_task(bind=True)
def poll_solution(grader_client, solution_id):
    grader_client.poll_grader(solution_id)
