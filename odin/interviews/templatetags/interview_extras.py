from statistics import mean
from decimal import Decimal

from django import template
from django.utils import timezone
from django.db.models import Q

register = template.Library()


@register.filter(name='calculate_average_rating')
def calculate_average_rating(interview):
    data = [
        interview.code_skills_rating,
        interview.code_design_rating,
        interview.fit_attitude_rating
    ]
    return f'{Decimal(mean(data)):.{3}}'


@register.filter(name='has_interviews_access')
def has_interviews_access(user):
    current_date = timezone.now().date()
    if user.is_superuser:
        return True
    elif user.is_interviewer():
        conditions = (
            {
                'start_date__lte': current_date
            },
            {
                'end_interview_date__gte': current_date
            }
        )

        qs = user.interviewer.courses_to_interview.filter(Q(**conditions[0]) & Q(**conditions[1]))

        return qs.exists()

    return False
