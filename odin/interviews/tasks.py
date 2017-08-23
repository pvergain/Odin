from celery import shared_task

from odin.applications.models import ApplicationInfo
from odin.education.services import add_student
from odin.education.models import Student


@shared_task(bind=True)
def assign_accepted_users_to_courses(self):
    active_application_infos = ApplicationInfo.objects.get_open_for_interview()
    for info in active_application_infos:
        accepted = info.accepted_applicants
        for application in accepted:
            if not application.user.is_student():
                student = Student.objects.create_from_user(application.user)
            else:
                student = application.user.student

            add_student(course=info.course, student=student)
