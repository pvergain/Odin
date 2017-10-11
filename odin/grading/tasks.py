from __future__ import absolute_import, unicode_literals
from celery import shared_task

from requests.exceptions import Timeout, ConnectionError

from django.conf import settings
from django.apps import apps

from .client import GraderClient
from .helper import get_grader_ready_data
from .exceptions import PollingError


@shared_task(bind=True, max_retries=None)
def poll_solution(self, solution_id, solution_model):
    grader_client = GraderClient(solution_model_repr=solution_model,
                                 settings_module=settings,
                                 grader_ready_data={})
    try:
        grader_client.poll_grader(solution_id)
    except PollingError as exc:
        raise self.retry(exc=exc, countdown=settings.GRADER_POLLING_COUNTDOWN)


@shared_task(bind=True, max_retries=None)
def submit_solution(self, solution_id, solution_model):
    solution_model_repr = solution_model
    solution_model = apps.get_model(solution_model)
    grader_ready_data = get_grader_ready_data(solution_id, solution_model)
    grader_client = GraderClient(solution_model_repr=solution_model_repr,
                                 settings_module=settings,
                                 grader_ready_data=grader_ready_data)
    try:
        grader_client.submit_request_to_grader(solution_id, poll_solution)
    except (Timeout, ConnectionError) as exc:
        raise self.retry(exc=exc, countdown=settings.GRADER_RESUBMIT_COUNTDOWN)
