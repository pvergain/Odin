from django.utils import timezone


def json_field_default():
    return {}


def get_now():
    return timezone.now()
