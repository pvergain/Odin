from django import template

register = template.Library()


@register.filter(name='render_message')
def get_message(msg):
    return msg.message.strip("[]'")


@register.filter(name='lookup')
def lookup(dictionary, key, default=0):
    return dictionary.get(key, default)


@register.simple_tag(name='active', takes_context=True)
def active(context, pattern):
    request = context.get('request')
    url_name = request.resolver_match.url_name
    if pattern.split(':')[-1] == url_name:
        return 'start active open'

    return ''
