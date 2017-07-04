from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Course, Teacher
from .services import add_teacher


@receiver(post_save, sender=Course)
def populate_course_teachers_with_superusers(sender, instance, created, **kwargs):
    if created:
        superusers = Teacher.objects.filter(is_superuser=True)
        for user in superusers:
            add_teacher(instance, user)
