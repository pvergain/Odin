from django import template

register = template.Library()


@register.filter(name='render_message')
def get_message(msg):
    return msg.message.strip("[]'")
