import uuid

from datetime import timedelta
from dateutil import rrule

from django.db import models
from django.core.exceptions import ValidationError

from odin.common.models import UpdatedAtCreatedAtModelMixin
from odin.common.utils import get_now

from odin.users.models import BaseUser

from .managers import StudentManager, TeacherManager


class Student(BaseUser):
    user = models.OneToOneField(BaseUser, parent_link=True)

    objects = StudentManager()


class Teacher(BaseUser):
    user = models.OneToOneField(BaseUser, parent_link=True)
    hidden = models.BooleanField(default=False)

    objects = TeacherManager()


class Course(models.Model):
    name = models.CharField(unique=True, max_length=255)

    start_date = models.DateField()
    end_date = models.DateField()

    students = models.ManyToManyField(Student,
                                      through='CourseAssignment',
                                      through_fields=('course', 'student'))

    teachers = models.ManyToManyField(Teacher,
                                      through='CourseAssignment',
                                      through_fields=('course', 'teacher'))

    slug_url = models.SlugField(null=True, unique=True)

    repository = models.URLField(blank=True)
    video_channel = models.URLField(blank=True)
    facebook_group = models.URLField(blank=True)

    generate_certificates_delta = models.DurationField(default=timedelta(days=15))

    @property
    def duration_in_weeks(self):
        weeks = rrule.rrule(
            rrule.WEEKLY,
            dtstart=self.start_date,
            until=self.end_date
        )
        return weeks.count()

    @property
    def has_started(self):
        now = get_now()

        return self.start_date <= now.date()

    @property
    def has_finished(self):
        now = get_now()

        return self.end_date <= now.date()

    @property
    def can_generate_certificates(self):
        now = get_now()

        return now.date() <= self.end_date + self.generate_certificates_delta

    def __str__(self) -> str:
        return self.name


class CourseDescription(models.Model):
    course = models.OneToOneField(Course, related_name='description')
    verbose = models.TextField(blank=True)


class CourseAssignment(models.Model):
    student = models.ForeignKey(Student,
                                on_delete=models.CASCADE,
                                related_name='course_assignments',
                                blank=True, null=True)
    teacher = models.ForeignKey(Teacher,
                                on_delete=models.CASCADE,
                                related_name='course_assignments',
                                blank=True, null=True)

    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='course_assignments')

    class Meta:
        unique_together = (('teacher', 'course'), ('student', 'course'))

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

    def clean(self):
        if self.student is None and self.teacher is None:
            raise ValidationError('Provide one of student / teacher')


class BaseMaterial(UpdatedAtCreatedAtModelMixin, models.Model):
    identifier = models.CharField(unique=True, max_length=255)
    url = models.URLField(blank=True)
    content = models.TextField(blank=True)

    class Meta:
        abstract = True


class Material(BaseMaterial, models.Model):
    pass


class IncludedMaterial(BaseMaterial, models.Model):
    material = models.ForeignKey(Material,
                                 on_delete=models.CASCADE,
                                 related_name='included_materials')
    topic = models.ForeignKey('Topic',
                              on_delete=models.CASCADE,
                              related_name='materials')


class Week(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    number = models.PositiveIntegerField(default=1)
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='weeks',
                               blank=True,
                               null=True)


class Topic(UpdatedAtCreatedAtModelMixin, models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='topics')
    week = models.ForeignKey(Week,
                             on_delete=models.CASCADE,
                             related_name='topics')


class Lecture(models.Model):
    date = models.DateField()

    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='lectures')
    week = models.ForeignKey(Week,
                             on_delete=models.CASCADE,
                             related_name='lectures')

    present_students = models.ManyToManyField(Student, related_name='lectures')

    @property
    def not_present_students(self):
        present_ids = self.present_students.values_list('id', flat=True)

        return self.course.students.exclude(id__in=present_ids)


class Certificate(models.Model):
    assignment = models.OneToOneField(CourseAssignment,
                                      on_delete=models.CASCADE)
    token = models.CharField(default=uuid.uuid4, unique=True, max_length=110)


class StudentNote(UpdatedAtCreatedAtModelMixin, models.Model):
    assignment = models.ForeignKey(CourseAssignment,
                                   on_delete=models.CASCADE,
                                   related_name='notes')
    author = models.ForeignKey(Teacher,
                               on_delete=models.CASCADE,
                               related_name='notes')

    text = models.TextField(blank=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Note for {self.assignment.student}'
