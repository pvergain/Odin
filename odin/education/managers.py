from django.db.models import Manager, Q
from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils import timezone

from odin.users.managers import UserManager
from odin.users.models import BaseUser


class BaseEducationUserManager(UserManager):
    def create(self, **kwargs):
        return self.create_user(**kwargs)


class StudentManager(BaseEducationUserManager):
    def create_from_user(self, user: BaseUser):
        Student = apps.get_model('education', 'Student')

        if user.downcast(Student) is not None:
            raise ValidationError('Student already exists')

        user._state.adding = False

        if not user.is_active:
            user.is_active = True
            user.save()

        student = Student(user_id=user.id)
        student.__dict__.update(user.__dict__)

        student.save()

        return Student.objects.get(id=student.id)


class TeacherManager(BaseEducationUserManager):
    def create_from_user(self, user: BaseUser):
        Teacher = apps.get_model('education', 'Teacher')

        if user.downcast(Teacher) is not None:
            raise ValidationError('Teacher already exists')

        user._state.adding = False

        if not user.is_active:
            user.is_active = True
            user.save()

        student = Teacher(user_id=user.id)
        student.__dict__.update(user.__dict__)

        student.save()

        return Teacher.objects.get(id=student.id)


class CourseManager(Manager):
    def get_active_for_interview(self):
        current_date = timezone.now().date()
        conditions = (
            {
                'application_info__start_interview_date__lte': current_date
            },
            {
                'application_info__end_interview_date__gte': current_date
            }
        )

        return self.filter(Q(**conditions[0]) & Q(**conditions[1]))

    def get_active_courses(self):
        return self.filter(start_date__lte=timezone.now().date(),
                           end_date__gte=timezone.now().date())

    def get_closed_courses(self):
        return self.filter(end_date__lte=timezone.now().date())
