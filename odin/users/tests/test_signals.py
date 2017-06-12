import os

from test_plus import TestCase

from ..models import Profile
from ..factories import BaseUserFactory

from odin.common.faker import faker


class ProfileSignalTests(TestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    def test_create_user_creates_profile(self):
        self.assertEqual(Profile.objects.count(), 0)
        BaseUserFactory()
        self.assertEqual(Profile.objects.count(), 1)

    def test_sign_up_request_creates_profile(self):
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
        self.assertEqual(Profile.objects.count(), 1)
