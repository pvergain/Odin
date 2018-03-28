from test_plus import TestCase

from odin.users.factories import BaseUserFactory

from django.test import Client
from django.shortcuts import reverse

from odin.common.faker import faker

client = Client()


class LoginApiTest(TestCase):
    def setUp(self):
        self.test_password = faker.password()
        self.test_email = faker.email()
        self.user = BaseUserFactory(email=self.test_email)
        self.user.set_password(self.test_password)
        self.user.is_active = True
        self.user.save()
        self.login_url = reverse('api:auth:login')

    def test_user_cannot_login_with_wrong_email(self):
        email = faker.email()
        data = {
            'email': email,
            'password': self.test_password,
        }

        response = client.post(self.login_url, data=data)

        self.assertEqual(response.status_code, 400)

    def test_user_cannot_login_with_wrong_password(self):
        password = faker.password()
        data = {
            'email': self.user.email,
            'password': password,
        }

        response = client.post(self.login_url, data=data)

        self.assertEqual(response.status_code, 400)

    def test_user_cannot_login_if_account_is_inactive(self):
        self.user.is_active = False
        self.user.save()

        data = {
            'email': self.user.email,
            'password': self.test_password,
        }

        response = client.post(self.login_url, data=data)

        self.assertEqual(response.status_code, 400)

    def test_user_can_login_when_account_is_active(self):
        data = {
            'email': self.user.email,
            'password': self.test_password,
        }

        response = self.post(self.login_url, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['me']['email'], self.user.email)
