from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.dispatch import receiver

from allauth.account.signals import email_confirmed
from allauth.socialaccount.signals import social_account_added

from ..users.models import BaseUser, Profile
from .services import process_social_account


@receiver(post_save, sender=BaseUser)
def create_profile_upon_user_creation(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(email_confirmed)
def social_accounts_process_on_confirmation(request, *args, **kwargs):
    user_instance = get_object_or_404(BaseUser, email=kwargs.get('email_address').email)
    profile_instance = user_instance.profile
    process_social_account(user_instance, profile_instance)


@receiver(social_account_added)
def social_accounts_process_on_add(request, sociallogin, **kwargs):
    user_instance = sociallogin.user
    profile_instance = user_instance.profile
    process_social_account(user_instance, profile_instance)
