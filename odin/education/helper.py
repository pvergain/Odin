from odin.common.utils import get_now

from .models import Lecture


def get_dates_for_weeks(course):
    week_dates = {}
    lectures = course.lectures.filter(week__isnull=False).all()

    for lecture in lectures:
        week_number = lecture.week.number
        if week_number not in week_dates:
            week_dates[week_number] = [lecture.date]
        else:
            week_dates[week_number].append(lecture.date)

    return week_dates


def percentage_presence(user_dates, course):
    lecture_dates = Lecture.objects.filter(course=course,
                                           date__lte=get_now().date()).values_list('date', flat=True)
    user_dates = [date for date in user_dates if date in lecture_dates]

    percentage = int((len(user_dates) / len(lecture_dates)) * 100)

    return f'{percentage} %'
