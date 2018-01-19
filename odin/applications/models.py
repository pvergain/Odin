from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.apps import apps

from odin.education.models import Course

from odin.users.models import BaseUser

from .managers import ApplicationInfoManager
from .query import ApplicationQuerySet


class ApplicationInfo(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    course = models.OneToOneField(Course, related_name='application_info')

    start_interview_date = models.DateField(blank=True, null=True)
    end_interview_date = models.DateField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    external_application_form = models.URLField(
        blank=True, null=True,
        help_text='Only add if course requires external application form'
    )

    objects = ApplicationInfoManager()

    def __str__(self):
        return "{0}".format(self.course)

    @property
    def accepted_applicants(self):
        return self.applications.select_related('user__profile').filter(is_accepted=True)

    def apply_is_active(self):
        return self.start_date <= timezone.now().date() <= self.end_date

    def interview_is_active(self):
        return self.start_interview_date <= timezone.now().date() and \
               self.end_interview_date >= timezone.now().date()

    def clean(self):
        if self.course.start_date < timezone.now().date():
            raise ValidationError(f"{self.course} has already started")

        if self.start_date < timezone.now().date() or self.end_date < timezone.now().date():
            raise ValidationError("Can not create an application in the past")

        if self.start_date >= self.end_date:
            raise ValidationError("Start date can not be after end date")

        if self.start_interview_date and self.end_interview_date:
            if self.start_interview_date < timezone.now().date() or self.end_interview_date <= timezone.now().date():
                raise ValidationError("Can not create interview dates in the past")

            if self.start_interview_date >= self.end_interview_date:
                raise ValidationError("Start interview date can not be after end interview date")

    @property
    def has_competition(self):
        return hasattr(self, 'competition')


class Application(models.Model):
    application_info = models.ForeignKey(ApplicationInfo, related_name='applications')
    user = models.ForeignKey(BaseUser, related_name='applications')

    phone = models.CharField(null=True, blank=True, max_length=255)
    skype = models.CharField(max_length=255)
    works_at = models.CharField(null=True, blank=True, max_length=255)
    studies_at = models.CharField(blank=True, null=True, max_length=255)
    has_interview_date = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    objects = ApplicationQuerySet.as_manager()

    def get_interview(self):
        interview = self.interview_set.select_related('interviewer__profile')
        if interview:
            return self.interview_set.select_related('interviewer__profile').first()

    def __str__(self):
        return "{0} applying to {1}".format(self.user, self.application_info)

    class Meta:
        unique_together = (("application_info", "user"),)

    def clean(self):
        if not self.application_info.apply_is_active():
            raise ValidationError(f"The application period for {self.application_info.course} has expired!")

    @property
    def is_completed(self):
        """
        TODO: Add a bunch of nice tests
        """
        Solution = apps.get_model('competitions', 'Solution')

        if not self.application_info.has_competition:
            return True

        tasks = {
            task: False
            for task in self.application_info.competition.tasks.all()
        }

        solutions = Solution.objects.filter(
            participant=self.user,
            task__competition=self.application_info.competition,
            status=Solution.OK
        )

        for solution in solutions:
            if solution.task in tasks:
                tasks[solution.task] = True

        return all(tasks.values())
