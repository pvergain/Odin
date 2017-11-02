from typing import Dict

from django.core.exceptions import ValidationError

from .models import BaseUser, Profile
from .helper import check_macs_for_student


def update_user_profile(*,
                        user: BaseUser,
                        data: Dict[str, str]) -> Profile:
    if data:
        mac = data.get('mac')

        user.profile.full_name = data.get('full_name')
        user.profile.description = data.get('description')
        user.profile.avatar = data.get('avatar')
        user.profile.mac = mac
        user.social_accounts = data.get('social_accounts')

        user.profile.full_clean()
        user.profile.save()

        if mac:
            check_macs_for_student(user, mac)

    return user.profile


def create_user(*,
                email: str,
                registration_uuid: str=None,
                password: str=None,
                profile_data: Dict[str, str]=None) -> BaseUser:

    if BaseUser.objects.filter(email=email).exists():
        raise ValidationError('User already exists.')

    user = BaseUser.objects.create(email=email, password=password)
    user.registration_uuid = registration_uuid
    user.save()

    update_user_profile(user=user, data=profile_data)

    return user
