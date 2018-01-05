from test_plus import TestCase

from ..templatetags.application_extras import has_solution_for_task

from odin.users.factories import BaseUserFactory
from odin.competitions.factories import CompetitionFactory, CompetitionTaskFactory, SolutionFactory
from odin.competitions.models import CompetitionParticipant

from ..factories import ApplicationInfoFactory, ApplicationFactory


class TestHasSolutionForTask(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()
        self.competition = CompetitionFactory()
        self.competition_task = CompetitionTaskFactory(competition=self.competition, gradable=False)
        self.application_info = ApplicationInfoFactory(competition=self.competition)
        self.application = ApplicationFactory(user=self.user, application_info=self.application_info)

    def test_no_users_are_returned_when_no_users_have_solution_for_task(self):
        self.assertFalse(has_solution_for_task(self.competition_task, self.application))

    def test_user_is_returned_when_he_or_she_has_correct_solution_for_task(self):
        participant = CompetitionParticipant.objects.create_from_user(self.user)
        SolutionFactory(task=self.competition_task, participant=participant)
        self.assertTrue(has_solution_for_task(self.competition_task, self.application))
