from test_plus import TestCase

from django.urls import reverse
from django.utils import timezone

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory, SuperUserFactory
from odin.education.models import Material
from odin.education.factories import (
    MaterialFactory,
    ProgrammingLanguageFactory,
    TaskFactory,
    IncludedTaskFactory
)

from ..models import (
    CompetitionMaterial,
    CompetitionJudge,
    Competition,
    CompetitionTask,
    CompetitionTest,
    CompetitionParticipant,
    Solution
)
from ..factories import (
    CompetitionFactory,
    CompetitionJudgeFactory,
    CompetitionParticipantFactory,
    CompetitionMaterialFactory,
    CompetitionTaskFactory,
    CompetitionTestFactory
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


class TestEditCompetitionView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.competition = CompetitionFactory()
        self.user = BaseUserFactory(password=self.test_password)
        self.judge = CompetitionJudge.objects.create_from_user(user=self.user)
        self.url = reverse('competitions:edit-competition',
                           kwargs={
                               'competition_slug': self.competition.slug_url
                           })

    def test_access_to_url_forbidden_if_not_judge(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(url_name=self.url)
            self.response_403(response)

    def test_post_to_url_forbidden_if_not_judge(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(url_name=self.url, data={})
            self.response_403(response)

    def test_can_access_edit_competition_successfully_if_judge(self):
        self.competition.judges.add(self.judge)
        self.competition.save()
        with self.login(email=self.judge.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)

    def test_initial_data_is_shown_in_form(self):
        self.competition.judges.add(self.judge)
        self.competition.save()
        with self.login(email=self.judge.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)
            form = response.context.get('form')
            self.assertEqual(self.competition.name, form.initial.get('name'))
            self.assertEqual(self.competition.start_date, form.initial.get('start_date'))
            self.assertEqual(self.competition.end_date, form.initial.get('end_date'))
            self.assertEqual(self.competition.slug_url, form.initial.get('slug_url'))


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


class TestCreateExistingCompetitionMaterialFromExistingView(TestCase):
    def setUp(self):
        self.competition = CompetitionFactory()
        self.material = CompetitionMaterialFactory(competition=self.competition)
        self.url = reverse('competitions:create-competition-material-from-existing',
                           kwargs={
                               'competition_slug': self.competition.slug_url
                           })
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.judge = CompetitionJudge.objects.create_from_user(user=self.user)

    def test_get_is_forbidden_if_not_judge_for_competition(self):
        user = BaseUserFactory(password=self.test_password)
        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url)
            self.response_403(response)

    def test_get_is_allowed_when_judge_for_competition(self):
        self.competition.judges.add(self.judge)
        self.competition.save()

        with self.login(email=self.judge.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)

    def test_can_add_included_material_from_existing_included_materials(self):
        competition = CompetitionFactory()
        self.competition.judges.add(self.judge)
        self.competition.save()
        competition_material = CompetitionMaterialFactory(competition=competition)

        competition_material_count = CompetitionMaterial.objects.count()
        material_count = Material.objects.count()

        with self.login(email=self.judge.email, password=self.test_password):
            response = self.post(self.url, data={'material': competition_material.material.id})
            self.assertRedirects(response, expected_url=reverse(
                'competitions:competition-detail',
                kwargs={'competition_slug': self.competition.slug_url}))
            self.assertEqual(competition_material_count + 1, CompetitionMaterial.objects.count())
            self.assertEqual(material_count, Material.objects.count())

    def test_can_add_ordinary_material_to_competition(self):
        material_count = CompetitionMaterial.objects.count()
        material = MaterialFactory()
        self.competition.judges.add(self.judge)
        self.competition.save()
        with self.login(email=self.judge.email, password=self.test_password):
            response = self.post(self.url, data={'material': material.id})
            self.assertRedirects(response, expected_url=reverse(
                                 'competitions:competition-detail',
                                 kwargs={'competition_slug': self.competition.slug_url}))
            self.assertEqual(material_count + 1, CompetitionMaterial.objects.count())


class TestEditCompetitionMaterialView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.competition = CompetitionFactory()
        self.competition_material = CompetitionMaterialFactory(competition=self.competition)
        self.user = BaseUserFactory(password=self.test_password)
        self.judge = CompetitionJudge.objects.create_from_user(user=self.user)
        self.url = reverse('competitions:edit-competition-material',
                           kwargs={
                               'competition_slug': self.competition.slug_url,
                               'material_id': self.competition_material.id
                           })

    def test_access_to_url_forbidden_if_not_judge(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(url_name=self.url)
            self.response_403(response)

    def test_post_to_url_forbidden_if_not_judge(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(url_name=self.url, data={})
            self.response_403(response)

    def test_can_access_edit_competition_successfully_if_judge(self):
        self.competition.judges.add(self.judge)
        self.competition.save()
        with self.login(email=self.judge.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)

    def test_initial_data_is_shown_in_form(self):
        self.competition.judges.add(self.judge)
        self.competition.save()
        with self.login(email=self.judge.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)
            form = response.context.get('form')
            self.assertEqual(self.competition_material.identifier, form.initial.get('identifier'))
            self.assertEqual(self.competition_material.url, form.initial.get('url'))
            self.assertEqual(self.competition_material.content, form.initial.get('content'))


class TestCreateNewCompetitionTaskView(TestCase):
    def setUp(self):
        self.competition = CompetitionFactory()
        self.url = reverse('competitions:create-new-competition-task',
                           kwargs={
                               'competition_slug': self.competition.slug_url
                           })
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.judge = CompetitionJudge.objects.create_from_user(self.user)
        self.language = ProgrammingLanguageFactory()

    def test_can_not_access_view_when_not_judge_in_competition(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.response_403(response)

    def test_can_create_new_task_if_judge_in_competition(self):
        self.competition.judges.add(self.judge)
        task_count = CompetitionTask.objects.count()

        data = {
            'name': faker.name(),
            'description': faker.text()
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            expected_url = reverse('competitions:competition-detail',
                                   kwargs={
                                       'competition_slug': self.competition.slug_url
                                   })
            self.assertRedirects(response, expected_url=expected_url)
            self.assertEqual(task_count + 1, CompetitionTask.objects.count())

    def test_can_not_create_new_task_if_not_judge_in_competition(self):
        task_count = CompetitionTask.objects.count()
        data = {
            'name': faker.name(),
            'description': faker.text()
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)

            self.response_403(response)
            self.assertEqual(task_count, CompetitionTask.objects.count())

    def test_post_does_not_create_test_when_task_is_not_gradable(self):
        self.competition.judges.add(self.judge)
        task_count = CompetitionTask.objects.count()
        test_count = CompetitionTest.objects.count()

        data = {
            'name': faker.name(),
            'description': faker.text(),
            'gradable': False,
            'language': self.language.id,
            'code': faker.text()
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            expected_url = reverse('competitions:competition-detail',
                                   kwargs={
                                       'competition_slug': self.competition.slug_url
                                   })
            self.assertRedirects(response, expected_url=expected_url)
            self.assertEqual(task_count + 1, CompetitionTask.objects.count())
            self.assertEqual(test_count, CompetitionTest.objects.count())

    def test_post_creates_test_when_task_is_gradable(self):
        self.competition.judges.add(self.judge)
        task_count = CompetitionTask.objects.count()
        test_count = CompetitionTest.objects.count()

        data = {
            'name': faker.name(),
            'description': faker.text(),
            'gradable': True,
            'language': self.language.id,
            'code': faker.text()
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            expected_url = reverse('competitions:competition-detail',
                                   kwargs={
                                       'competition_slug': self.competition.slug_url
                                   })
            self.assertRedirects(response, expected_url=expected_url)
            self.assertEqual(task_count + 1, CompetitionTask.objects.count())
            self.assertEqual(test_count + 1, CompetitionTest.objects.count())


class TestCreateCompetitionTaskFromExistingView(TestCase):
    def setUp(self):
        self.competition = CompetitionFactory()
        self.url = reverse('competitions:create-competition-task-from-existing',
                           kwargs={
                               'competition_slug': self.competition.slug_url
                           })
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.judge = CompetitionJudge.objects.create_from_user(self.user)
        self.language = ProgrammingLanguageFactory()

    def test_can_not_access_view_when_not_judge_in_competition(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.response_403(response)

    def test_can_add_existing_task_that_has_not_been_added_to_competition(self):
        self.competition.judges.add(self.judge)
        task_count = CompetitionTask.objects.count()
        existing_task = TaskFactory()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data={'task': existing_task.id})
            expected_url = reverse('competitions:competition-detail',
                                   kwargs={
                                       'competition_slug': self.competition.slug_url
                                   })
            self.assertRedirects(response, expected_url=expected_url)
            self.assertEqual(task_count + 1, Competition.objects.count())

    def test_can_add_existing_task_that_has_already_been_added_to_competition(self):
        existing_task = CompetitionTaskFactory()
        self.competition.judges.add(self.judge)
        task_count = CompetitionTask.objects.count()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data={'task': existing_task.task.id})
            expected_url = reverse('competitions:competition-detail',
                                   kwargs={
                                       'competition_slug': self.competition.slug_url
                                   })
            self.assertRedirects(response, expected_url=expected_url)
            self.assertEqual(task_count + 1, Competition.objects.count())

    def test_can_add_existing_task_that_has_been_included_in_course(self):
        existing_task = IncludedTaskFactory()
        self.competition.judges.add(self.judge)
        task_count = CompetitionTask.objects.count()

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data={'task': existing_task.task.id})
            expected_url = reverse('competitions:competition-detail',
                                   kwargs={
                                       'competition_slug': self.competition.slug_url
                                   })
            self.assertRedirects(response, expected_url=expected_url)
            self.assertEqual(task_count + 1, Competition.objects.count())


class TestEditCompetitionTaskView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.competition = CompetitionFactory()
        self.competition_task = CompetitionTaskFactory(competition=self.competition)
        self.user = BaseUserFactory(password=self.test_password)
        self.judge = CompetitionJudge.objects.create_from_user(user=self.user)
        self.url = reverse('competitions:edit-competition-task',
                           kwargs={
                               'competition_slug': self.competition.slug_url,
                               'task_id': self.competition_task.id
                           })

    def test_access_to_url_forbidden_if_not_judge(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(url_name=self.url)
            self.response_403(response)

    def test_post_to_url_forbidden_if_not_judge(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(url_name=self.url, data={})
            self.response_403(response)

    def test_can_access_edit_competition_successfully_if_judge(self):
        self.competition.judges.add(self.judge)
        self.competition.save()
        with self.login(email=self.judge.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)

    def test_initial_data_is_shown_in_form(self):
        self.competition.judges.add(self.judge)
        self.competition.save()
        with self.login(email=self.judge.email, password=self.test_password):
            response = self.get(self.url)
            self.response_200(response)
            form = response.context.get('form')
            self.assertEqual(self.competition_task.name, form.initial.get('name'))
            self.assertEqual(self.competition_task.description, form.initial.get('description'))
            self.assertEqual(self.competition_task.gradable, form.initial.get('gradable'))


class TestCreateGradableSolutionApiView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.competition = CompetitionFactory()
        self.task = CompetitionTaskFactory(competition=self.competition, gradable=True)
        self.participant = CompetitionParticipant.objects.create_from_user(self.user)
        self.competition.participants.add(self.participant)
        self.language = ProgrammingLanguageFactory()
        self.url = reverse('competitions:submit-gradable-solution',
                           kwargs={
                               'competition_slug': self.competition.slug_url,
                               'task_id': self.task.id
                           })

    def test_get_is_not_allowed(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)

            self.response_405(response)

    def test_redirects_to_login_when_anonoymous(self):
        data = {
            'participant': self.participant.id,
            'code': faker.text(),
            'task': self.task.id
        }
        response = self.post(self.url, data=data)
        self.response_302(response)

    def test_forbidden_when_user_is_not_a_participant_in_competition(self):
        new_user = BaseUserFactory(password=self.test_password)
        new_user.is_active = True
        new_user.save()

        data = {
            'participant': self.participant.id,
            'code': faker.text(),
            'task': self.task.id
        }

        with self.login(email=new_user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.response_403(response)

    def test_does_not_create_solution_when_task_has_no_test(self):
        solutions_count = Solution.objects.count()
        data = {
            'participant': self.participant.id,
            'code': faker.text(),
            'task': self.task.id
        }

        with self.login(email=self.user.email, password=self.test_password):
            self.post(self.url, data=data)
            self.assertEqual(solutions_count, Solution.objects.count())

    def test_creates_solution_when_participant_in_competition_and_task_has_test(self):
        CompetitionTestFactory(task=self.task)
        solutions_count = Solution.objects.count()
        data = {
            'participant': self.participant.id,
            'code': faker.text(),
            'task': self.task.id
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.response_201(response)
            self.assertEqual(solutions_count + 1, Solution.objects.count())

    def test_created_solution_is_in_task_solutions(self):
        CompetitionTestFactory(task=self.task)
        solutions_count = Solution.objects.count()
        data = {
            'participant': self.participant.id,
            'code': faker.text(),
            'task': self.task.id
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.response_201(response)
            self.assertEqual(solutions_count + 1, Solution.objects.count())
            self.task.refresh_from_db()
            solution = Solution.objects.last()
            self.assertIn(solution, self.task.solutions.all())

    def test_post_with_different_task_does_not_overwrite_task_from_url(self):
        CompetitionTestFactory(task=self.task)
        solutions_count = Solution.objects.count()
        data = {
            'participant': self.participant.id,
            'code': faker.text(),
            'task': faker.pyint()
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.response_201(response)
            self.assertEqual(solutions_count + 1, Solution.objects.count())
            solution = Solution.objects.last()
            self.assertEqual(solution.task.id, self.task.id)

    def test_post_with_different_participant_does_not_overwrite_request_participant(self):
        CompetitionTestFactory(task=self.task)
        solutions_count = Solution.objects.count()
        data = {
            'participant': faker.pyint(),
            'code': faker.text(),
            'task': self.task.id
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.response_201(response)
            self.assertEqual(solutions_count + 1, Solution.objects.count())
            solution = Solution.objects.last()
            self.assertEqual(solution.participant.id, self.participant.id)


class TestCreateNonGradableCompetitionSolutionView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.competition = CompetitionFactory()
        self.task = CompetitionTaskFactory(competition=self.competition, gradable=False)
        self.participant = CompetitionParticipant.objects.create_from_user(self.user)
        self.competition.participants.add(self.participant)
        self.language = ProgrammingLanguageFactory()
        self.url = reverse('competitions:submit-non-gradable-solution',
                           kwargs={
                               'competition_slug': self.competition.slug_url,
                               'task_id': self.task.id
                           })

    def test_get_is_not_allowed(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)

            self.response_405(response)

    def test_creates_solution_when_participant_in_competition(self):
        solutions_count = Solution.objects.count()
        data = {
            'participant': self.participant.id,
            'url': faker.url(),
            'task': self.task.id
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.response_201(response)
            self.assertEqual(solutions_count + 1, Solution.objects.count())

    def test_created_solution_is_in_task_solutions(self):
        solutions_count = Solution.objects.count()
        data = {
            'participant': self.participant.id,
            'url': faker.url(),
            'task': self.task.id
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.response_201(response)
            self.assertEqual(solutions_count + 1, Solution.objects.count())
            self.task.refresh_from_db()
            solution = Solution.objects.last()
            self.assertIn(solution, self.task.solutions.all())

    def test_post_with_different_task_does_not_overwrite_task_from_url(self):
        solutions_count = Solution.objects.count()
        data = {
            'participant': self.participant.id,
            'url': faker.url(),
            'task': faker.pyint()
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.response_201(response)
            self.assertEqual(solutions_count + 1, Solution.objects.count())
            solution = Solution.objects.last()
            self.assertEqual(solution.task.id, self.task.id)

    def test_post_with_different_participant_does_not_overwrite_request_participant(self):
        solutions_count = Solution.objects.count()
        data = {
            'participant': faker.pyint(),
            'url': faker.url(),
            'task': self.task.id
        }

        with self.login(email=self.user.email, password=self.test_password):
            response = self.post(self.url, data=data)
            self.response_201(response)
            self.assertEqual(solutions_count + 1, Solution.objects.count())
            solution = Solution.objects.last()
            self.assertEqual(solution.participant.id, self.participant.id)
