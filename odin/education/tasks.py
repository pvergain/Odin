from celery import shared_task

from .models import Course, CheckIn


@shared_task(name='calculate_presence')
def calculate_presence():
    active_courses = Course.objects.get_active_courses()

    for course in active_courses:
        course_assignments = course.course_assignments.all()
        lectures = course.lectures.values_list('date', flat=True)

        if lectures:
            for course_assignment in course_assignments:
                user = course_assignment.user
                all_user_checkins = CheckIn.objects.get_user_dates(user=user, course=course).filter(
                                                                            date__in=lectures)

                percentage_presence = int((len(all_user_checkins) / len(lectures)) * 100)
                course_assignment.student_presence = percentage_presence
                course_assignment.save()
