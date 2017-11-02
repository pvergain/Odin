from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField

from odin.common.models import UpdatedAtCreatedAtModelMixin
from odin.users.models import BaseUser
from odin.education.models import BaseMaterial, BaseTask, BaseTest, Material, Task, Test
from odin.education.mixins import TestModelMixin

from .managers import CompetitionJudgeManager, CompetitionParticipantManager


class CompetitionParticipant(BaseUser):
    user = models.OneToOneField(BaseUser, parent_link=True)

    objects = CompetitionParticipantManager()


class CompetitionJudge(BaseUser):
    user = models.OneToOneField(BaseUser, parent_link=True)

    objects = CompetitionJudgeManager()


class Competition(models.Model):
    name = models.CharField(unique=True, max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    participants = models.ManyToManyField(CompetitionParticipant)
    judges = models.ManyToManyField(CompetitionJudge)

    slug_url = models.SlugField(unique=True)

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("End date cannot be before start date!")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_application_competition(self):
        return hasattr(self, 'application_info')

    def __str__(self):
        return self.name


class CompetitionMaterial(BaseMaterial):
    material = models.ForeignKey(Material,
                                 on_delete=models.CASCADE,
                                 related_name='competition_materials')
    competition = models.ForeignKey(Competition,
                                    on_delete=models.CASCADE,
                                    related_name='materials')

    class Meta:
        unique_together = (('competition', 'material'),)


class CompetitionTask(BaseTask):
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE,
                             related_name='competition_tasks')
    competition = models.ForeignKey(Competition,
                                    on_delete=models.CASCADE,
                                    related_name='tasks')

    class Meta:
        unique_together = (('competition', 'task'),)


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
    participant = models.ForeignKey(CompetitionParticipant, related_name='solutions')
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


class CompetitionTest(TestModelMixin, BaseTest):
    task = models.OneToOneField(CompetitionTask,
                                on_delete=models.CASCADE,
                                related_name='test')
    test = models.ForeignKey(Test,
                             on_delete=models.CASCADE,
                             related_name='competition_tests')
