from odin.interviews.helpers.interviews import GenerateInterviews, GenerateInterviewSlots
from odin.applications.models import ApplicationInfo
from celery import shared_task


@shared_task(bind=True)
def generate_interview_slots(self):

    interview_length = 20
    break_between_interviews = 10

    interview_slots_generator = GenerateInterviewSlots(interview_length, break_between_interviews)

    interview_slots_generator.generate_interview_slots()
    interview_slots_generator.get_generated_slots()

    courses_to_interview = ApplicationInfo.objects.get_open_for_interview()

    if len(courses_to_interview) == 0:
        print('There are no open for interview courses!\n')
        print('No interviews will be generated.')

    for info in courses_to_interview:
        interview_generator = GenerateInterviews(application_info=info)
        app_without_interviews = interview_generator.get_applications_without_interviews()
        free_interview_slots = interview_generator.get_free_interview_slots()
        if app_without_interviews > free_interview_slots:
            continue

        interview_generator.generate_interviews()
