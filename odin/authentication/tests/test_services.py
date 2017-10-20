from test_plus import TestCase
from allauth.socialaccount.models import SocialAccount

from odin.users.factories import BaseUserFactory
from odin.authentication.services import process_social_account
from odin.common.faker import faker


class TestProcessSocialAccount(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()

    def test_process_social_account_does_not_add_anything_to_profile_if_no_user_social_accounts(self):
        process_social_account(user=self.user, profile=self.user.profile)
        self.assertEqual({}, self.user.profile.social_accounts)

    def test_process_social_account_adds_a_social_account_to_user_profile_if_it_exists(self):
        url = faker.url()
        data = {
            'html_url': url
        }
        social_account = SocialAccount.objects.create(user=self.user, provider="github", extra_data=data)
        self.user.socialaccount_set.add(social_account)
        self.user.save()
        process_social_account(user=self.user, profile=self.user.profile)
        self.assertEqual({"GitHub": url}, self.user.profile.social_accounts)
