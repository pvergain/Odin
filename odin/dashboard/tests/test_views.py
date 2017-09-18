from test_plus import TestCase
from unittest import skip

from django.core.urlresolvers import reverse

from odin.users.factories import BaseUserFactory

from odin.common.faker import faker


class TestRedirectToDashboardIndexView(TestCase):
    def setUp(self):
        self.url = '/'
        self.test_password = faker.password()

    @skip("Temporary for competition")
    def test_get_redirects_to_login_when_no_user_logged(self):
        response = self.get(self.url, follow=True)
        expected = reverse('account_login') + '?next=/dashboard/'
        self.assertRedirects(response=response, expected_url=expected)

    @skip("Temporary for competition")
    def test_get_redirects_to_dashboard_index_when_user_logged(self):
        user = BaseUserFactory(password=self.test_password)
        user.is_active = True
        user.save()

        with self.login(email=user.email, password=self.test_password):
            response = self.get(self.url, follow=True)
            self.assertRedirects(response=response, expected_url=self.reverse('dashboard:index'))
