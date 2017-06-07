from django.db.models.signals import post_save
from django.dispatch import receiver

from ..users.models import BaseUser, Profile


@receiver(post_save, sender=BaseUser)
def create_user_callback(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
