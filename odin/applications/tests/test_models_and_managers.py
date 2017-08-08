from test_plus import TestCase

from django.utils import timezone

from odin.common.faker import faker
from odin.applications.models import ApplicationInfo
from odin.applications.factories import ApplicationInfoFactory


class ApplicationInfoTests(TestCase):

    def setUp(self):
        self.start_date = timezone.now().date()
        self.end_date = timezone.now().date() + timezone.timedelta(days=2)
        self.open_applications = ApplicationInfoFactory.create_batch(size=5,
                                                                     start_date=self.start_date,
                                                                     end_date=self.end_date,
                                                                     start_interview_date=self.start_date,
                                                                     end_interview_date=self.end_date)

        false_start_date = timezone.now().date() - timezone.timedelta(days=2)
        false_end_date = timezone.now().date() - timezone.timedelta(days=1)
        self.closed_applications = ApplicationInfoFactory.create_batch(
                                      size=5,
                                      start_date=false_start_date,
                                      end_date=false_end_date,
                                      start_interview_date=false_start_date,
                                      end_interview_date=false_end_date)

    def test_get_open_for_apply_returns_only_open_applications(self):

        applications = ApplicationInfo.objects.get_open_for_apply()
        self.assertEqual(applications, self.open_applications)

    def test_get_closed_for_apply_returns_only_closed_applications(self):
        applications = ApplicationInfo.objects.get_closed_for_apply()
        self.assertEqual(applications, self.closed_applications)

    def test_get_ordered_closed_application_infos_returns_sorted_closed_applications(self):
        # Randomize end dates
        for app_info in self.closed_applications:
            app_info.end_date -= timezone.timedelta(days=faker.pyint())
            app_info.save()

        self.closed_applications = sorted(self.closed_applications, key=lambda x: x.end_date, reverse=True)
        applications = ApplicationInfo.objects.get_ordered_closed_application_infos()
        self.assertEqual(applications, self.closed_applications)

    def test_get_open_for_interview_returns_only_open_for_interview_applications(self):
        applications = ApplicationInfo.objects.get_open_for_interview()
        self.assertEqual(applications, self.open_applications)
