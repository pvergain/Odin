from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BaseUser, Profile


@receiver(post_save, sender=BaseUser)
def create_profile_upon_user_creation(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
