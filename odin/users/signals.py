from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.dispatch import receiver
from allauth.account.signals import email_confirmed

from .models import BaseUser, Profile


@receiver(post_save, sender=BaseUser)
def create_user_callback(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(email_confirmed)
def social_accounts_process(request, *args, **kwargs):
    user_instance = get_object_or_404(BaseUser, email=kwargs.get('email_address').email)
    profile_instance = user_instance.profile
    if any(user_instance.socialaccount_set.all()):
        for acc in user_instance.socialaccount_set.all():
            provider = acc.get_provider()
            pair = {provider.name: acc.extra_data.get('html_url', None)}
            profile_instance.social_accounts.update(pair)
        profile_instance.save()
