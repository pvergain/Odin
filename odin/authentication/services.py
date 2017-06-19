from odin.users.models import BaseUser, Profile


def process_social_account(user: BaseUser, profile: Profile) -> None:
    if user.socialaccount_set.count() != 0:
        for acc in user.socialaccount_set.all():
            provider = acc.get_provider()
            pair = {provider.name: acc.extra_data.get('html_url', None)}
            profile.social_accounts.update(pair)
        profile.save()
