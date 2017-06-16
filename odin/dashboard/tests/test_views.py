from test_plus import TestCase
from django.core.urlresolvers import reverse

from odin.users.factories import BaseUserFactory
from odin.education.models import Student, Teacher

from odin.common.faker import faker


class TestRedirectToDashboardIndexView(TestCase):

    def setUp(self):
        self.url = '/'
        self.test_password = faker.password()

    def test_get_redirects_to_login_when_no_user_logged(self):
        response = self.get(self.url, follow=True)
        expected = reverse('account_login') + '?next=/dashboard/'
        self.assertRedirects(response=response, expected_url=expected)

    def test_get_redirects_to_dashboard_index_when_user_logged(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.save()

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url, follow=True)
            self.assertRedirects(response=response, expected_url=self.reverse('dashboard:index'))


class TestManagementView(TestCase):

    def setUp(self):
        self.url = self.reverse('dashboard:management')
        self.test_password = faker.password()

    def test_user_passes_test_when_not_superuser(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.save()

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(403, response.status_code)

    def test_user_passes_test_when_superuser(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.is_superuser = True
        user.save()

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)

    def test_can_make_student_or_teacher_if_user_is_not_student_or_teacher(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.is_superuser = True
        user.save()

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertContains(response, "Make Student")
            self.assertContains(response, "Make Teacher")

    def test_can_not_make_student_if_user_is_already_student(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.is_superuser = True
        user.save()

        Student.objects.create_from_user(user)

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertNotContains(response, "Make Student")
            self.assertContains(response, "Make Teacher")

    def test_can_not_make_student_if_user_is_already_student(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.is_superuser = True
        user.save()

        Teacher.objects.create_from_user(user)

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)
            self.assertNotContains(response, "Make Teacher")
            self.assertContains(response, "Make Student")
