import mistune

from django import template

register = template.Library()


@register.filter(name='markdown')
def convert_from_markdown(text):
    md = mistune.Markdown()
    return md(text)
