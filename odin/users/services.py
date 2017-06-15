
def get_gh_email_address(request):
    socialaccount = request.session.get('socialaccount_sociallogin', {})
    email_address = socialaccount.get('email_addresses', None)
    if email_address is not None:
        return email_address[0].get('email', '')


def process_social_account(user, profile, **kwargs):
    if any(user.socialaccount_set.all()):
        for acc in user.socialaccount_set.all():
            provider = acc.get_provider()
            pair = {provider.name: acc.extra_data.get('html_url', None)}
            profile.social_accounts.update(pair)
        profile.save()
