from django.urls import reverse

from test_plus import TestCase

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory


class TestPersonalProfileView(TestCase):
    def setUp(self):
        self.url = self.reverse('dashboard:users:profile')
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.user.is_active = True
        self.user.save()

    def test_get_redirects_to_login_when_not_signed_in(self):
        response = self.get(self.url)
        expected = self.reverse('account_login') + '?next=' + self.url
        self.assertRedirects(response=response, expected_url=expected)

    def test_get_ok_when_signed_in(self):
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(self.url)
            self.assertEqual(200, response.status_code)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.user = BaseUserFactory(password=self.test_password)
        self.user.is_active = True
        self.user.save()

    def test_get_forbidden_when_user_is_not_superuser(self):
        test_user = BaseUserFactory()
        url = reverse('dashboard:users:profile-by-email', kwargs={'user_email': test_user.email})
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(url_name=url)
            self.assertEqual(403, response.status_code)

    def test_get_ok_when_user_is_superuser(self):
        test_user = BaseUserFactory()
        self.user.is_superuser = True
        self.user.save()
        url = reverse('dashboard:users:profile-by-email', kwargs={'user_email': test_user.email})
        with self.login(email=self.user.email, password=self.test_password):
            response = self.get(url_name=url)
            self.assertEqual(200, response.status_code)
