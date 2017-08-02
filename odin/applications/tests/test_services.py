from test_plus import TestCase

from django.utils import timezone
from django.core.exceptions import ValidationError

from odin.common.faker import faker
from odin.education.factories import CourseFactory
from odin.users.factories import BaseUserFactory
from odin.applications.models import (
    Application,
    ApplicationInfo,
    ApplicationTask,
    IncludedApplicationTask,
    ApplicationSolution
)
from odin.applications.services import (
    create_application,
    create_application_info,
    create_included_application_task,
    create_application_solution
)
from odin.applications.factories import (
    ApplicationInfoFactory,
    ApplicationFactory,
    IncludedApplicationTaskFactory,
    ApplicationSolutionFactory
)


class TestCreateApplicationInfoService(TestCase):
    def setUp(self):
        self.start_date = faker.date_object()
        self.end_date = faker.date_object()
        self.course = CourseFactory()
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
            create_application(application_info=self.app_info, user=self.user)

    def test_create_application_raises_validation_error_when_user_has_already_applied(self):
        ApplicationFactory(application_info=self.app_info, user=self.user)

        with self.assertRaises(ValidationError):
            create_application(application_info=self.app_info, user=self.user)

    def test_create_application_creates_application_when_application_is_active_and_user_has_not_applied(self):
        current_application_count = Application.objects.count()

        create_application(application_info=self.app_info, user=self.user)

        self.assertEqual(current_application_count + 1, Application.objects.count())


class TestCreateIncludedApplicationTaskService(TestCase):
    def setUp(self):
        self.app_info = ApplicationInfoFactory()
        self.task_name = faker.word()
        self.task_description = faker.text()

    def test_create_included_application_task_creates_only_included_task_when_existing_is_provided(self):
        existing_task = ApplicationTask.objects.create(name=self.task_name, description=self.task_description)
        current_app_task_count = ApplicationTask.objects.count()
        current_included_app_task_count = IncludedApplicationTask.objects.count()

        create_included_application_task(existing_task=existing_task, application_info=self.app_info)

        self.assertEqual(current_app_task_count, ApplicationTask.objects.count())
        self.assertEqual(current_included_app_task_count + 1, IncludedApplicationTask.objects.count())

    def test_create_included_application_task_creates_task_and_included_task_when_no_existing_is_provided(self):
        current_app_task_count = ApplicationTask.objects.count()
        current_included_app_task_count = IncludedApplicationTask.objects.count()

        create_included_application_task(name=self.task_name,
                                         description=self.task_description,
                                         application_info=self.app_info)

        self.assertEqual(current_app_task_count + 1, ApplicationTask.objects.count())
        self.assertEqual(current_included_app_task_count + 1, IncludedApplicationTask.objects.count())

    def test_create_included_application_task_raises_validation_error_when_task_has_external_form(self):
        self.app_info.external_application_form = faker.url()
        self.app_info.save()
        with self.assertRaises(ValidationError):
            create_included_application_task(name=self.task_name,
                                             description=self.task_description,
                                             application_info=self.app_info)

    def test_create_application_task_rasies_validation_error_when_task_is_already_added(self):
        task = IncludedApplicationTaskFactory(name=self.task_name,
                                              description=self.task_description,
                                              application_info=self.app_info)

        with self.assertRaises(ValidationError):
            create_included_application_task(application_info=self.app_info, existing_task=task.task)


class TestCreateApplicationSolutionService(TestCase):
    def setUp(self):
        self.user = BaseUserFactory()
        self.user.is_active = True
        self.user.save()
        self.app_info = ApplicationInfoFactory()
        self.task = IncludedApplicationTaskFactory(application_info=self.app_info)
        self.application = ApplicationFactory(user=self.user, application_info=self.app_info)
        self.solution = ApplicationSolutionFactory(task=self.task, application=self.application)

    def test_create_application_solution_updates_solutions_when_instance_is_provided(self):
        previous_url = self.solution.url
        new_url = str(faker.pyint()) + faker.url()
        current_solution_count = ApplicationSolution.objects.count()
        create_application_solution(task=self.task,
                                    application=self.application,
                                    url=new_url)
        self.assertEqual(current_solution_count, ApplicationSolution.objects.count())
        self.solution.refresh_from_db()
        self.assertNotEqual(previous_url, self.solution.url)
        self.assertEqual(new_url, self.solution.url)
