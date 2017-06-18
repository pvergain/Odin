def get_gh_email_address(request):
    """
    COMMENT:
    This is definetely not a service. Looks like a util for the allauth view.
    """
    socialaccount = request.session.get('socialaccount_sociallogin', {})
    email_address = socialaccount.get('email_addresses', None)
    if email_address is not None:
        return email_address[0].get('email', '')
