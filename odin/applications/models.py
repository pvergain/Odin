from django.utils import timezone

from django.db import models

from odin.education.models import Course
from odin.users.models import BaseUser
from .managers import ApplicationInfoManager
from .query import ApplicationQuerySet


class ApplicationInfo(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    course = models.ForeignKey(Course)
    start_interview_date = models.DateField(blank=False, null=True)
    end_interview_date = models.DateField(blank=False, null=True)

    description = models.TextField(
        blank=True,
        null=True,
        help_text='Това описва процедурата по кандидатстване. Излиза тук /apply/edit/<course-url>'
    )

    external_application_form = models.URLField(blank=True, null=True,
                                                help_text='Only add if course requires external application form')

    objects = ApplicationInfoManager()

    def __str__(self):
        return "{0}".format(self.course)

    def apply_is_active(self):
        return self.end_date >= timezone.now().date()

    def interview_is_active(self):
        return self.start_interview_date <= timezone.now().date() and \
               self.end_interview_date >= timezone.now().date()


class Application(models.Model):
    application_info = models.ForeignKey(ApplicationInfo)
    user = models.ForeignKey(BaseUser)

    phone = models.CharField(null=True, blank=True, max_length=255)
    skype = models.CharField(null=True, blank=True, max_length=255)
    works_at = models.CharField(null=True, blank=True, max_length=255)
    studies_at = models.CharField(blank=True, null=True, max_length=255)
    has_interview_date = models.BooleanField(default=False)

    objects = ApplicationQuerySet.as_manager()

    def __str__(self):
        return "{0} applying to {1}".format(self.user, self.application_info)

    class Meta:
        unique_together = (("application_info", "user"),)
