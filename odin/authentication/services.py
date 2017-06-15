def process_social_account(user, profile, **kwargs):
    if any(user.socialaccount_set.all()):
        for acc in user.socialaccount_set.all():
            provider = acc.get_provider()
            pair = {provider.name: acc.extra_data.get('html_url', None)}
            profile.social_accounts.update(pair)
        profile.save()
