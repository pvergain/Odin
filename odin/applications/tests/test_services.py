from test_plus import TestCase

from django.utils import timezone
from django.core.exceptions import ValidationError

from odin.common.faker import faker
from odin.education.factories import CourseFactory
from odin.users.factories import BaseUserFactory
from odin.competitions.factories import CompetitionFactory
from odin.applications.models import (
    Application,
    ApplicationInfo,
)
from odin.applications.services import (
    create_application,
    create_application_info,
)
from odin.applications.factories import (
    ApplicationInfoFactory,
    ApplicationFactory,
)


class TestCreateApplicationInfoService(TestCase):
    def setUp(self):
        self.start_date = faker.date_object()
        self.end_date = faker.date_object()
        self.course = CourseFactory(start_date=timezone.now().date(),
                                    end_date=timezone.now().date() + timezone.timedelta(days=1))
        self.start_interview_date = faker.date_object()
        self.end_interview_date = faker.date_object()

    def test_create_application_info_raises_validation_error_when_start_date_is_in_past(self):
        self.start_date = timezone.now().date() - timezone.timedelta(days=1)
        self.end_date = timezone.now().date() + timezone.timedelta(days=1)

        with self.assertRaises(ValidationError):
            create_application_info(start_date=self.start_date,
                                    end_date=self.end_date,
                                    course=self.course)

    def test_create_application_info_raises_validation_error_when_end_date_is_in_past(self):
        self.start_date = timezone.now().date() + timezone.timedelta(days=1)
        self.end_date = timezone.now().date() - timezone.timedelta(days=1)

        with self.assertRaises(ValidationError):
            create_application_info(start_date=self.start_date,
                                    end_date=self.end_date,
                                    course=self.course)

    def test_create_application_info_raises_validation_error_when_start_date_is_after_end_date(self):
        self.start_date = timezone.now().date() + timezone.timedelta(days=2)
        self.end_date = timezone.now().date() + timezone.timedelta(days=1)

        with self.assertRaises(ValidationError):
            create_application_info(start_date=self.start_date,
                                    end_date=self.end_date,
                                    course=self.course)

    def test_create_application_info_raises_validation_error_when_start_interview_date_is_in_past(self):
        self.start_date = timezone.now().date() + timezone.timedelta(days=1)
        self.end_date = timezone.now().date() + timezone.timedelta(days=2)

        self.start_interview_date = timezone.now().date() - timezone.timedelta(days=1)
        self.end_interview_date = timezone.now().date() + timezone.timedelta(days=1)

        with self.assertRaises(ValidationError):
            create_application_info(start_date=self.start_date,
                                    end_date=self.end_date,
                                    course=self.course,
                                    start_interview_date=self.start_interview_date,
                                    end_interview_date=self.end_interview_date)

    def test_create_application_info_raises_validation_error_when_end_interview_date_is_in_past(self):
        self.start_date = timezone.now().date() + timezone.timedelta(days=1)
        self.end_date = timezone.now().date() + timezone.timedelta(days=2)

        self.start_interview_date = timezone.now().date() + timezone.timedelta(days=1)
        self.end_interview_date = timezone.now().date() - timezone.timedelta(days=1)

        with self.assertRaises(ValidationError):
            create_application_info(start_date=self.start_date,
                                    end_date=self.end_date,
                                    course=self.course,
                                    start_interview_date=self.start_interview_date,
                                    end_interview_date=self.end_interview_date)

    def test_create_application_info_raises_validation_error_when_start_interview_date_is_after_end_date(self):
        self.start_date = timezone.now().date() + timezone.timedelta(days=1)
        self.end_date = timezone.now().date() + timezone.timedelta(days=2)

        self.start_interview_date = timezone.now().date() + timezone.timedelta(days=2)
        self.end_interview_date = timezone.now().date() + timezone.timedelta(days=1)

        with self.assertRaises(ValidationError):
            create_application_info(start_date=self.start_date,
                                    end_date=self.end_date,
                                    course=self.course,
                                    start_interview_date=self.start_interview_date,
                                    end_interview_date=self.end_interview_date)

    def test_create_application_info_creates_application_info_when_data_is_valid(self):
        self.start_date = timezone.now().date() + timezone.timedelta(days=1)
        self.end_date = timezone.now().date() + timezone.timedelta(days=2)

        self.start_interview_date = timezone.now().date() + timezone.timedelta(days=1)
        self.end_interview_date = timezone.now().date() + timezone.timedelta(days=2)

        current_app_info_count = ApplicationInfo.objects.count()

        create_application_info(start_date=self.start_date,
                                end_date=self.end_date,
                                course=self.course,
                                start_interview_date=self.start_interview_date,
                                end_interview_date=self.end_interview_date)

        self.assertEqual(current_app_info_count + 1, ApplicationInfo.objects.count())

    def test_create_application_info_raises_validation_error_when_course_has_started(self):
        self.course.start_date = timezone.now().date() - timezone.timedelta(days=faker.pyint())
        with self.assertRaises(ValidationError):
            create_application_info(start_date=self.start_date,
                                    end_date=self.end_date,
                                    course=self.course,
                                    start_interview_date=self.start_interview_date,
                                    end_interview_date=self.end_interview_date)


class TestCreateApplicationService(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.app_info = ApplicationInfoFactory(course=self.course,
                                               start_date=timezone.now().date(),
                                               end_date=timezone.now().date()+timezone.timedelta(days=1))
        self.user = BaseUserFactory()

    def test_create_application_raises_validation_error_when_application_is_inactive(self):
        self.app_info.end_date -= timezone.timedelta(days=2)
        self.app_info.save()

        with self.assertRaises(ValidationError):
            create_application(application_info=self.app_info, user=self.user, full_name=faker.name())

    def test_create_application_raises_validation_error_when_user_has_already_applied(self):
        ApplicationFactory(application_info=self.app_info, user=self.user)

        with self.assertRaises(ValidationError):
            create_application(application_info=self.app_info, user=self.user, full_name=faker.name())

    def test_create_application_creates_application_when_application_is_active_and_user_has_not_applied(self):
        current_application_count = Application.objects.count()

        create_application(application_info=self.app_info, user=self.user, skype=faker.word(), full_name=faker.name())

        self.assertEqual(current_application_count + 1, Application.objects.count())

    def test_create_application_makes_user_participant(self):
        competition = CompetitionFactory()
        self.app_info.competition = competition
        self.app_info.save()

        create_application(application_info=self.app_info, user=self.user, skype=faker.word(), full_name=faker.name())

        self.assertEqual(1, competition.participants.count())
        self.assertEqual(self.user, competition.participants.first())

    def test_create_application_adds_user_as_participant_to_competition_if_app_info_has_competition(self):
        competition = CompetitionFactory()
        self.app_info.competition = competition
        self.app_info.save()
        create_application(application_info=self.app_info, user=self.user, skype=faker.word(), full_name=faker.name())

        self.assertTrue(competition.participants.filter(email=self.user.email).exists())
