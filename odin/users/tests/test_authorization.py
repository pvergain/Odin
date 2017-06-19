from odin.common.faker import faker

from test_plus import TestCase

from ..models import BaseUser

from ..factories import BaseUserFactory

import os


class AuthorizationTests(TestCase):
    """
    COMMENT: This looks like a test for the authentication app?
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    def test_user_registration_with_recaptcha_passed(self):
        self.assertEqual(BaseUser.objects.count(), 0)
        url = self.reverse('account_signup')
        password = "1234asdf"
        data = {
            'email': faker.email(),
            'password1': password,
            'password2': password,
            'g-recaptcha-response': 'PASSED'
        }
        response = self.post(url_name=url, data=data, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BaseUser.objects.count(), 1)

    def test_user_registration_with_recaptcha_not_passed(self):
        self.assertEqual(BaseUser.objects.count(), 0)
        url = self.reverse('account_signup')
        password = "1234asdf"
        data = {
            'email': faker.email(),
            'password1': password,
            'password2': password,
        }
        response = self.post(url_name=url, data=data, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BaseUser.objects.count(), 0)

    def test_user_registration_for_already_logged_in_user(self):
        user = BaseUserFactory(password="1234asdf")
        user.is_active = True
        user.save()
        self.assertEqual(BaseUser.objects.count(), 1)
        with self.login(email=user.email, password="1234asdf"):
            url = self.reverse('account_signup')
            response = self.get(url_name=url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(BaseUser.objects.count(), 1)
