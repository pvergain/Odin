from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BaseUser, Profile

from odin.education.models import Teacher, Course
from odin.education.services import add_teacher


@receiver(post_save, sender=BaseUser)
def create_profile_upon_user_creation(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=BaseUser)
def make_new_superuser_teacher(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            teacher = Teacher.objects.create_from_user(instance)
            teacher.save()
            for course in Course.objects.all():
                add_teacher(course, teacher, hidden=True)
