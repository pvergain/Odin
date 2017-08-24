import uuid

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from odin.users.models import BaseUser

from odin.applications.models import ApplicationInfo, Application

from .managers import InterviewerManager, InterviewManager
from .query import InterviewQuerySet


class Interviewer(BaseUser):
    user = models.OneToOneField(BaseUser, parent_link=True)
    courses_to_interview = models.ManyToManyField(ApplicationInfo)
    interviews = models.ManyToManyField(Application, through='Interview')
    skype = models.CharField(null=True, blank=True, max_length=255)

    objects = InterviewerManager()


class InterviewerFreeTime(models.Model):
    INTERVIEW_TIME_CHOICES = (
        (20, '20 minutes'),
        (25, '25 minutes'),
        (30, '30 minutes'),
    )

    BREAK_TIME_CHOICES = (
        (5, '5 minutes'),
        (10, '10 minutes'),
        (15, '15 minutes'),
    )

    interviewer = models.ForeignKey(Interviewer, related_name='free_time_slots')
    date = models.DateField(blank=False, null=True)
    start_time = models.TimeField(blank=False, null=True)
    end_time = models.TimeField(blank=False, null=True)
    interview_time_length = models.SmallIntegerField(choices=INTERVIEW_TIME_CHOICES,
                                                     default=20)
    break_time = models.SmallIntegerField(choices=BREAK_TIME_CHOICES,
                                          default=5)

    def __str__(self):
        return f'On {self.date} - from {self.start_time} to {self.end_time}'

    def has_generated_slots(self):
        return self.interviews.exists()

    def clean(self):
        if self.date < timezone.now().date():
            raise ValidationError("Your free time slot can not be in the past")
        if self.start_time >= self.end_time:
            raise ValidationError("The start time can not be the same or after the end time")

        user_timeslots_for_date = InterviewerFreeTime.objects.filter(interviewer=self.interviewer, date=self.date)
        if not user_timeslots_for_date.exists():
            return
        for slot in user_timeslots_for_date:
            if max(slot.start_time, self.start_time) <= min(slot.end_time, self.end_time):
                raise ValidationError("Times are overlapping with an already existing Free Time Slot")

    def save(self, *args, **kwargs):
        self.full_clean()

        return super().save(*args, **kwargs)


class Interview(models.Model):
    interviewer = models.ForeignKey(Interviewer)
    application = models.ForeignKey(Application, null=True)
    date = models.DateField(blank=False, null=True)
    start_time = models.TimeField(blank=False, null=True)
    end_time = models.TimeField(blank=False, null=True)
    interviewer_time_slot = models.ForeignKey(InterviewerFreeTime, related_name="interviews", default=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    interviewer_comment = models.TextField(null=True, blank=True, help_text="Коментар от интервюиращия")

    possible_ratings = [(i, i) for i in range(11)]
    code_skills_rating = models.IntegerField(
        default=0,
        choices=possible_ratings,
        help_text='Оценка върху уменията на кандидата да пише'
        ' код и върху знанията му за базови алгоритми')
    code_design_rating = models.IntegerField(
        default=0,
        choices=possible_ratings,
        help_text='Оценка върху уменията на кандидата да "съставя'
        ' програми", да разбива нещата на парчета + базово OOP')
    fit_attitude_rating = models.IntegerField(
        default=0,
        choices=possible_ratings,
        help_text='Оценка на интервюиращия в зависимост от'
        ' усета му за човека (подходящ ли е за курса?)')

    has_confirmed = models.BooleanField(default=False)
    has_received_email = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    objects = InterviewManager.from_queryset(InterviewQuerySet)()

    def __str__(self):
        return f"Interview on {self.date}, starting at {self.start_time} and ending on {self.end_time}"

    def delete(self, *args, **kwargs):
        if self.has_confirmed:
            raise ValidationError("Can not delete an already confirmed interview")

        return super().delete(*args, **kwargs)

    def reset(self):
        self.application = None
        self.has_received_email = False
        self.has_confirmed = False

        self.save()

    def active_date(self):
        return timezone.now().date() <= self.date
