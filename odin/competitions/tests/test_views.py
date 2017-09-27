from test_plus import TestCase  # noqa

from django.urls import reverse
from django.utils import timezone

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory, SuperUserFactory

from ..models import CompetitionMaterial, CompetitionJudge, Competition
from ..factories import (
    CompetitionFactory,
    CompetitionJudgeFactory,
    CompetitionParticipantFactory,
)


class TestCompetitionDetailView(TestCase):

    def setUp(self):
        self.test_password = faker.password()
        self.competition = CompetitionFactory()
        self.user = BaseUserFactory(password=self.test_password)
        self.participant = CompetitionParticipantFactory(password=self.test_password)
        self.judge = CompetitionJudgeFactory(password=self.test_password)
        self.url = reverse('competitions:competition-detail', kwargs={'competition_slug': self.competition.slug_url})
        self.user.is_active = True
        self.participant.is_active = True
        self.judge.is_active = True
        self.user.save()
        self.participant.save()
        self.judge.save()

    def test_can_not_access_competition_detail_if_not_participant_or_judge(self):
        response = self.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_can_access_competition_detail_if_participant(self):
        self.competition.participants.add(self.participant)
        with self.login(email=self.participant.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_raises_404_when_competition_does_not_exist(self):
        url = reverse('competitions:competition-detail',
                      kwargs={
                          'competition_slug': self.competition.slug_url + str(faker.pyint())
                      })
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(url_name=url)
            self.response_404(response)


class TestCreateCompetitionView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.superuser = SuperUserFactory(password=self.test_password)
        self.url = reverse('competitions:create-competition')

    def test_access_to_url_forbidden_if_not_authenticated(self):
        response = self.get(self.url)
        self.response_403(response)

    def test_access_to_url_forbidden_if_authenticated_and_not_superuser(self):
        user = BaseUserFactory(password=self.test_password)

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url)
            self.response_403(response)

    def test_access_to_url_allowed_if_superuser(self):
        with self.login(email=self.superuser.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)

    def test_does_not_create_competition_when_end_date_is_after_start_date(self):
        competition_count = Competition.objects.count()
        start_date = timezone.now()
        end_date = start_date - timezone.timedelta(days=2)
        data = {
            'name': faker.name(),
            'start_date': start_date.date(),
            'end_date': end_date.date(),
            'slug_url': faker.slug()
        }

        with self.login(email=self.superuser.email, password=self.test_password):
            response = self.post(url_name=self.url, data=data)

            self.response_200(response)
            self.assertEqual(competition_count, Competition.objects.count())

    def test_creates_competition_when_data_is_valid(self):
        competition_count = Competition.objects.count()
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(days=2)

        data = {
            'name': faker.name(),
            'start_date': start_date.date(),
            'end_date': end_date.date(),
            'slug_url': faker.slug()
        }

        with self.login(email=self.superuser.email, password=self.test_password):
            response = self.post(url_name=self.url, data=data)

            self.response_302(response)
            self.assertEqual(competition_count + 1, Competition.objects.count())


class TestAddNewCompetitionMaterialView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.competition = CompetitionFactory()
        self.user = BaseUserFactory(password=self.test_password)
        self.judge = CompetitionJudge.objects.create_from_user(self.user)
        self.competition.judges.add(self.judge)
        self.url = reverse('competitions:create-new-competition-material',
                           kwargs={
                               'competition_slug': self.competition.slug_url
                           })

    def test_can_create_new_material_for_competition_if_judge(self):
        material_count = CompetitionMaterial.objects.count()
        data = {
            'identifier': faker.word(),
            'url': faker.url(),
            'content': faker.text()
        }
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            expected_url = reverse('competitions:competition-detail',
                                   kwargs={
                                       'competition_slug': self.competition.slug_url
                                   })
            self.assertRedirects(response, expected_url=expected_url)
            self.assertEqual(material_count + 1, CompetitionMaterial.objects.count())

    def test_post_for_not_existing_competition_returns_404(self):
        material_count = CompetitionMaterial.objects.count()
        data = {
            'identifier': faker.word(),
            'url': faker.url(),
            'content': faker.text()
        }
        url = reverse('competitions:create-new-competition-material',
                      kwargs={
                          'competition_slug': self.competition.slug_url + str(faker.pyint())
                      })
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(url, data=data)

            self.response_404(response)
            self.assertEqual(material_count, CompetitionMaterial.objects.count())

    def test_post_with_invalid_data_does_not_create_material(self):
        material_count = CompetitionMaterial.objects.count()
        data = {
            'url': faker.url(),
            'content': faker.text()
        }
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            self.response_200(response)
            self.assertEqual(material_count, CompetitionMaterial.objects.count())
