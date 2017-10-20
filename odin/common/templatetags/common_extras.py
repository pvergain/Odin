from django import template

register = template.Library()


@register.filter(name='render_message')
def get_message(msg):
    return msg.message.strip("[]'")


@register.filter(name='lookup')
def lookup(dictionary, key, default=0):
    return dictionary.get(key, default)
