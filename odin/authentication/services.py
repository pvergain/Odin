def process_social_account(user, profile, **kwargs):
    """
    COMMENT: We are not using **kwargs anywhere -> we don't need that
    Also, consider adding type anotations since this is a service.
    """
    if any(user.socialaccount_set.all()):
        for acc in user.socialaccount_set.all():
            provider = acc.get_provider()
            pair = {provider.name: acc.extra_data.get('html_url', None)}
            profile.social_accounts.update(pair)
        profile.save()
