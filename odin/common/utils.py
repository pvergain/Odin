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
