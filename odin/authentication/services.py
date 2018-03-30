from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models.query import Q
from django.db import transaction
from django.utils import timezone

from odin.emails.services import send_mail

from odin.users.models import (
    BaseUser,
    Profile,
    PasswordResetToken
)

from odin.education.models import (
    Student,
    Teacher,
    Course,
)


class _ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.FileField(source='full_image')

    class Meta:
        model = Profile
        fields = ('full_name', 'avatar')


class _UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUser
        fields = (
            'id',
            'email',
            )


STUDENT_TYPE = 'student'
TEACHER_TYPE = 'teacher'


def get_user_courses_per_user_type(*, user: BaseUser) -> str:
    teacher = user.downcast(Teacher)
    student = user.downcast(Student)

    teacher_courses = Course.objects.filter(
        teachers__in=[teacher]).values_list('id', flat=True)

    student_courses = Course.objects.filter(
        students__in=[student]).values_list('id', flat=True)

    return {
        STUDENT_TYPE: student_courses,
        TEACHER_TYPE: teacher_courses,
    }


def get_user_data(*, user: BaseUser):
    user_data = _UserSerializer(instance=user).data
    user_data['is_teacher'] = user.is_teacher()

    user_courses = get_user_courses_per_user_type(user=user)

    user_data['teacher_for_courses'] = user_courses[TEACHER_TYPE]
    user_data['student_for_courses'] = user_courses[STUDENT_TYPE]

    profile_data = _ProfileSerializer(instance=user.profile).data

    return {**user_data, **profile_data}


@transaction.atomic
def logout(*, user: BaseUser) -> BaseUser:
    user.rotate_secret_key()

    return user


@transaction.atomic
def initiate_reset_user_password(*, user: BaseUser) -> PasswordResetToken:
    if not user.is_active:
        raise ValidationError('Cannot reset password for inactive user')

    now = timezone.now()
    query = Q(user=user) & (Q(voided_at__isnull=True) | Q(used_at__isnull=True))
    PasswordResetToken.objects.filter(query).update(voided_at=now)

    token = PasswordResetToken.objects.create(user=user)

    reset_link = f'https://academy.hacksoft.io/forgot-password/{str(token.token)}/'

    send_mail(
        recipients=[user.email],
        template_name='account_email_password_reset_key',
        context={
            'password_reset_url': reset_link
        }
    )

    return token


@transaction.atomic
def reset_user_password(
    *,
    token: PasswordResetToken,
    password: str
) -> BaseUser:
    if token.used or token.voided:
        raise ValidationError('Invalid reset password token.')

    user = token.user

    validate_password(password)
    user.set_password(password)
    user.rotate_secret_key()

    user.save()

    token.use()

    return user


@transaction.atomic
def change_user_password(
    *,
    user: BaseUser,
    old_password: str,
    new_password: str,
) -> BaseUser:

    if not user.is_active:
        raise ValidationError('User account is disabled.')

    if not user.check_password(old_password):
        raise ValidationError('Old password is invalid.')

    validate_password(new_password)
    user.set_password(new_password)
    user.rotate_secret_key()

    user.save()

    return user
