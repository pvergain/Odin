from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField

from odin.common.models import UpdatedAtCreatedAtModelMixin

from odin.users.models import BaseUser

from odin.education.models import (
    Material,
    Task,
    Test,
    Course
)
from odin.education.mixins import TestModelMixin

from odin.applications.models import ApplicationInfo


class Competition(models.Model):
    name = models.CharField(unique=True, max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    participants = models.ManyToManyField(BaseUser, related_name='participant_in_competitions')
    judges = models.ManyToManyField(BaseUser, related_name='judge_in_competitions')

    slug_url = models.SlugField(unique=True)

    application_info = models.OneToOneField(
        ApplicationInfo,
        related_name='competition',
        blank=True, null=True
    )

    course = models.ForeignKey(
        Course,
        related_name='competitions',
        blank=True, null=True
    )

    def clean(self):
        """
        TODO: Add tests for validation errors
        """
        if self.start_date > self.end_date:
            raise ValidationError("End date cannot be before start date!")

        if self.course is not None and self.application_info is not None:
            raise ValidationError('Cannot have competition for both'
                                  'application & course')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_standalone(self):
        if self.application_info is None and self.course is None:
            return True

        return False

    def __str__(self):
        return self.name


class CompetitionMaterial(models.Model):
    material = models.ForeignKey(Material,
                                 on_delete=models.CASCADE,
                                 related_name='competition_materials')
    competition = models.ForeignKey(Competition,
                                    on_delete=models.CASCADE,
                                    related_name='materials')

    class Meta:
        unique_together = (('competition', 'material'),)


class CompetitionTask(models.Model):
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE,
                             related_name='competition_tasks')
    competition = models.ForeignKey(Competition,
                                    on_delete=models.CASCADE,
                                    related_name='tasks')

    class Meta:
        unique_together = (('competition', 'task'),)

    def __str__(self):
        return f'{self.task}, {self.competition}'

    @property
    def name(self):
        return self.task.name

    @property
    def description(self):
        return self.task.description

    @property
    def gradable(self):
        return self.task.gradable


class Solution(UpdatedAtCreatedAtModelMixin, models.Model):
    PENDING = 0
    RUNNING = 1
    OK = 2
    NOT_OK = 3
    SUBMITTED = 4
    MISSING = 5
    SUBMITTED_WITHOUT_GRADING = 6

    STATUS_CHOICE = (
        (PENDING, 'pending'),
        (RUNNING, 'running'),
        (OK, 'ok'),
        (NOT_OK, 'not_ok'),
        (SUBMITTED, 'submitted'),
        (MISSING, 'missing'),
        (SUBMITTED_WITHOUT_GRADING, 'submitted_without_grading'),
    )

    task = models.ForeignKey(CompetitionTask, related_name='solutions')
    participant = models.ForeignKey(BaseUser, related_name='competition_solutions')
    url = models.URLField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    check_status_location = models.CharField(max_length=128, null=True, blank=True)
    build_id = models.IntegerField(blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICE, default=SUBMITTED_WITHOUT_GRADING)
    test_output = JSONField(blank=True, null=True)
    return_code = models.IntegerField(blank=True, null=True)
    file = models.FileField(upload_to="solutions", blank=True, null=True)

    @property
    def verbose_status(self):
        return self.STATUS_CHOICE[self.status][1]

    class Meta:
        ordering = ['-id']


class CompetitionTest(TestModelMixin, models.Model):
    task = models.OneToOneField(CompetitionTask,
                                on_delete=models.CASCADE,
                                related_name='test')
    test = models.ForeignKey(Test,
                             on_delete=models.CASCADE,
                             related_name='competition_tests')

    def __str__(self):
        return f'{self.task}, {self.test}'

    @property
    def language(self):
        return self.test.language

    @property
    def extra_options(self):
        return self.test.extra_options

    @property
    def code(self):
        return self.test.code

    @property
    def file(self):
        return self.test.file

    @property
    def description(self):
        return self.test.description
