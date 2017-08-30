import mistune

from django import template

register = template.Library()


@register.filter(name='markdown')
def convert_from_markdown(text):
    md = mistune.Markdown()
    return md(text)


@register.filter(name='iterable_from_difference')
def iterable_from_difference(x, subtract_from):
    return range(subtract_from-x)
