import uuid

from datetime import timedelta
from dateutil import rrule

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField

from odin.common.models import UpdatedAtCreatedAtModelMixin
from odin.common.utils import get_now, json_field_default

from odin.users.models import BaseUser

from .managers import StudentManager, TeacherManager, CourseManager
from .query import TaskQuerySet, SolutionQuerySet
from .mixins import TestModelMixin


class Student(BaseUser):
    user = models.OneToOneField(BaseUser, parent_link=True)

    objects = StudentManager()


class Teacher(BaseUser):
    user = models.OneToOneField(BaseUser, parent_link=True)

    objects = TeacherManager()


class Course(models.Model):
    name = models.CharField(unique=True, max_length=255)

    start_date = models.DateField()
    end_date = models.DateField()

    attendable = models.BooleanField(default=True)

    students = models.ManyToManyField(
        Student,
        through='CourseAssignment',
        through_fields=('course', 'student')
    )

    teachers = models.ManyToManyField(
        Teacher,
        through='CourseAssignment',
        through_fields=('course', 'teacher')
    )

    slug_url = models.SlugField(unique=True)

    repository = models.URLField(blank=True)
    video_channel = models.URLField(blank=True, null=True)
    facebook_group = models.URLField(blank=True, null=True)

    logo = models.ImageField(blank=True, null=True)

    public = models.BooleanField(default=True)

    generate_certificates_delta = models.DurationField(default=timedelta(days=15))

    objects = CourseManager()

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("End date cannot be before start date!")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def visible_teachers(self):
        return self.teachers.filter(course_assignments__hidden=False).select_related('profile')

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

    def __str__(self):
        return self.verbose


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

    hidden = models.BooleanField(default=False)

    class Meta:
        unique_together = (('teacher', 'course'), ('student', 'course'))

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

    def clean(self):
        if self.student is None and self.teacher is None:
            raise ValidationError('Provide one of student / teacher')


class BaseMaterial(UpdatedAtCreatedAtModelMixin, models.Model):
    identifier = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    content = models.TextField(blank=True)

    class Meta:
        abstract = True


class Material(BaseMaterial):
    pass


class IncludedMaterial(BaseMaterial):
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='included_materials'
    )

    week = models.ForeignKey(
        'Week',
        related_name='materials',
        null=True,
    )

    course = models.ForeignKey(
        Course,
        related_name='included_materials',
        null=True,
    )

    class Meta:
        unique_together = (('week', 'material'), )


class Week(models.Model):

    start_date = models.DateField()
    end_date = models.DateField()

    number = models.PositiveIntegerField(default=1)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='weeks',
        null=True,
    )

    class Meta:
        ordering = ('number',)

    def __str__(self):
        return f'Week {self.number} - {self.course.name}'


class Lecture(models.Model):
    date = models.DateField()

    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='lectures')
    week = models.ForeignKey(Week,
                             on_delete=models.CASCADE,
                             related_name='lectures')

    present_students = models.ManyToManyField(Student, related_name='lectures')

    def clean(self):
        if hasattr(self, 'week'):
            if not self.week.start_date <= self.date <= self.week.end_date:
                raise ValidationError('Lecture date must be in the date range for it\'s week')

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

    text = models.TextField()

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Note for {self.assignment.student}'


class BaseTask(UpdatedAtCreatedAtModelMixin, models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    gradable = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Task(BaseTask):
    pass


class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=110)
    test_format = models.CharField(max_length=20, blank=True, null=True)
    requirements_format = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    def clean(self):
        if not self.test_format:
            raise ValidationError('Field test_format should not be blank')

        if not self.requirements_format:
            raise ValidationError('Field requirements_format should not be blank')

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)


class IncludedTask(BaseTask):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='included_tasks'
    )

    week = models.ForeignKey(
        Week,
        on_delete=models.CASCADE,
        related_name='included_tasks',
        null=True,
    )

    course = models.ForeignKey(
        Course,
        related_name='included_tasks',
        null=True,
    )

    objects = TaskQuerySet.as_manager()

    class Meta:
        unique_together = (('week', 'task'), )

    def __str__(self):
        return f'{self.id} - {self.name}'


class BaseTest(UpdatedAtCreatedAtModelMixin, models.Model):
    language = models.ForeignKey(ProgrammingLanguage)
    extra_options = JSONField(blank=True, null=True, default=json_field_default())
    code = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    file = models.FileField(blank=True, null=True)
    description = models.CharField(max_length=255, default='Test')

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.id}/{self.description}/{self.language}'


class Test(BaseTest):
    pass


class IncludedTest(TestModelMixin, BaseTest):
    task = models.OneToOneField(IncludedTask,
                                on_delete=models.CASCADE,
                                related_name='test')
    test = models.ForeignKey(Test,
                             on_delete=models.CASCADE,
                             related_name='included_tests')


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

    task = models.ForeignKey(IncludedTask, related_name='solutions')
    student = models.ForeignKey(Student, related_name='solutions')
    url = models.URLField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    check_status_location = models.CharField(max_length=128, null=True, blank=True)
    build_id = models.IntegerField(blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICE, default=SUBMITTED_WITHOUT_GRADING)
    test_output = JSONField(blank=True, null=True)
    return_code = models.IntegerField(blank=True, null=True)
    file = models.FileField(upload_to="solutions", blank=True, null=True)

    objects = SolutionQuerySet.as_manager()

    @property
    def verbose_status(self):
        return self.STATUS_CHOICE[self.status][1]

    def pass_or_fail_status(self):
        if self.task.gradable and self.status == self.OK or \
                not self.task.gradable and self.status == self.SUBMITTED_WITHOUT_GRADING:
            return "Passed"
        return "Failed"

    def __str__(self):
        return f'Solution for {self.task} with status {self.status}'

    class Meta:
        ordering = ['-id']


class SolutionComment(UpdatedAtCreatedAtModelMixin, models.Model):
    text = models.TextField()
    solution = models.ForeignKey(Solution, related_name='comments')
    user = models.ForeignKey(BaseUser, related_name='user_comments')
