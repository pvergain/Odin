from django import template

register = template.Library()


@register.filter
def index(items, i):
    return items[int(i)]


@register.filter
def get_key(items, key):
    return items[key]


@register.filter
def has_key(items, key):
    return key in items


@register.simple_tag
def call(obj, attr, *args):
    value = getattr(obj, attr)

    if callable(value):
        return value(*args)
