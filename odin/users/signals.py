from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.dispatch import receiver
from allauth.account.signals import email_confirmed

from .models import BaseUser, Profile
from .services import process_social_account


@receiver(post_save, sender=BaseUser)
def create_profile_upon_user_creation(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(email_confirmed)
def social_accounts_process(request, *args, **kwargs):
    user_instance = get_object_or_404(BaseUser, email=kwargs.get('email_address').email)
    profile_instance = user_instance.profile
    process_social_account(user_instance, profile_instance)
