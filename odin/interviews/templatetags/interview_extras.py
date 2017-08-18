from statistics import mean
from decimal import Decimal

from django import template

register = template.Library()


@register.filter(name='calculate_average_rating')
def calculate_average_rating(interview):
    data = [
        interview.code_skills_rating,
        interview.code_design_rating,
        interview.fit_attitude_rating
    ]
    return f'{Decimal(mean(data)):.{3}}'
