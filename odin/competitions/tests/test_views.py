from test_plus import TestCase  # noqa

from django.urls import reverse

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory

from ..models import CompetitionMaterial, CompetitionJudge
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
