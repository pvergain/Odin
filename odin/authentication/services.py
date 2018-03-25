from rest_framework import serializers

from django.core.exceptions import ValidationError
from django.db.models.query import Q
from django.db import transaction
from django.utils import timezone

from odin.emails.services import send_mail

from odin.users.models import BaseUser, Profile, PasswordResetToken


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


def get_user_type(*, user: BaseUser) -> str:
    STUDENT_TYPE = 'student'
    TEACHER_TYPE = 'teacher'

    if user.is_teacher():
        return TEACHER_TYPE
    elif user.is_student():
        return STUDENT_TYPE


def get_user_data(*, user: BaseUser):
    user_data = _UserSerializer(instance=user).data
    user_data['user_type'] = get_user_data(user)
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

    token = str(PasswordResetToken.objects.create(user=user).token)

    reset_link = f'https://academy.hacksoft.io/forgot-password/{token}/'

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

    user.set_password(password)
    user.rotate_secret_key()

    user.save()

    token.use()

    return user
