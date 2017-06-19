from django.utils import timezone


def json_field_default():
    return {}


def get_now():
    return timezone.now()


def get_readable_form_errors(form):
    """
    Provides an easier way to access form errors through templates.
    """
    if not form.is_valid():
        readable_errors = []
        for field, error in form.errors.items():
            readable_errors.extend(error)
    return readable_errors


def get_gh_email_address(request):
    """
    COMMENT:
    This is definetely not a service. Looks like a util for the allauth view.
    """
    socialaccount = request.session.get('socialaccount_sociallogin', {})
    email_address = socialaccount.get('email_addresses', None)
    if email_address is not None:
        return email_address[0].get('email', '')
