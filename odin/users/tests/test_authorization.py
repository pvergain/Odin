from odin.common.faker import faker

from test_plus import TestCase
from django.test import Client

from ..models import BaseUser

from ..factories import BaseUserFactory


class AuthorizationTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_user_registration(self):
        self.assertEqual(BaseUser.objects.count(), 0)
        url = self.reverse('account_signup')
        password = "1234asdf"
        data = {
            'email': faker.email(),
            'password1': password,
            'password2': password
        }
        response = self.post(url_name=url, data=data, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BaseUser.objects.count(), 1)

    def test_user_registration_for_already_logged_in_user(self):
        user = BaseUserFactory(password="1234asdf")
        user.is_active = True
        user.save()
        self.assertEqual(BaseUser.objects.count(), 1)
        with self.login(email=user.email, password="1234asdf"):
            url = self.reverse('account_signup')
            response = self.get(url_name=url, follow=True)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(BaseUser.objects.count(), 1)
