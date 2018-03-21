from inspect import signature

from django.conf import settings


MISSING_KEYWORD_ARGUMENT = '{}() is missing {} keyword-argument.'


def filter_kwargs(f, **kwargs):
    result = {}
    sig = signature(f)

    for param_name, param in sig.parameters.items():
        if param_name not in kwargs:
            if param.default is param.empty:
                raise TypeError(MISSING_KEYWORD_ARGUMENT.format(f.__name__, param_name))

            result[param_name] = param.default
        else:
            result[param_name] = kwargs[param_name]

    return result


def get_mandrill_api_key():
    api_key = settings.MANDRILL['MANDRILL_API_KEY']

    """
    There is a strange bug to investigate:
    env variable is parsed as tuple of one element.
    """
    if not isinstance(api_key, str):
        api_key = api_key[0]

    return api_key


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


def serialize_context(context):
    if context is None:
        context = {}

    for key in context:
        context[key] = str(context[key])

    return context
