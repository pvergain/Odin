from test_plus import TestCase

from django.utils import timezone

from odin.common.faker import faker
from odin.users.factories import SuperUserFactory
from odin.competitions.models import Competition


class TestPopulateCompetitionJudgesSignal(TestCase):
    def setUp(self):
        for i in range(5):
            SuperUserFactory()

    def test_create_competition_populates_judges_with_existing_superusers(self):
        start_date = faker.date_object()
        competition = Competition.objects.create(name=faker.word(),
                                                 start_date=start_date,
                                                 end_date=start_date + timezone.timedelta(faker.pyint()),
                                                 slug_url=faker.slug())

        self.assertEqual(5, competition.judges.count())
