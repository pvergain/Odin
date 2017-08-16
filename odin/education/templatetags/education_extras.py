import mistune

from django import template

from odin.education.services import get_presence_for_course

register = template.Library()


@register.filter(name='markdown')
def convert_from_markdown(text):
    md = mistune.Markdown()
    return md(text)


@register.filter(name='get_presence')
def get_course_presence(course, user):
    presence = get_presence_for_course(course=course, user=user)
    if presence:
        return presence.get('percentage_presence')
    return f'0 %'
