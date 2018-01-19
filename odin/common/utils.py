from django.utils import timezone

from rest_framework import serializers


def json_field_default():
    return {}


def get_now():
    return timezone.now()


def get_readable_form_errors(form):
    """
    Provides an easier way to access form errors through templates.
    """
    readable_errors = {}
    if not form.is_valid():
        for field, error in form.errors.items():
            if field == '__all__':
                readable_errors['Errors'] = error
            else:
                readable_errors[field] = error
    return readable_errors


def get_gh_email_address(request):
    socialaccount = request.session.get('socialaccount_sociallogin', {})
    email_address = socialaccount.get('email_addresses', None)
    if email_address is not None:
        return email_address[0].get('email', '')


def build_message(recipients, context):
    message = {
        'to': [],
        'global_merge_vars': [],
    }

    for mail in recipients:
        message['to'].append({'email': mail})

    for k, v in context.items():
        message['global_merge_vars'].append({'name': k, 'content': v})

    return message


def transfer_POST_data_to_dict(data):
    return {key: data.get(key) for key in data}


def create_serializer_class(name, fields):
    return type(name, (serializers.Serializer, ), fields)


def inline_serializer(*, fields, data=None, **kwargs):
    serializer_class = create_serializer_class(name='', fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)
