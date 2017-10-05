from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Competition, CompetitionJudge


@receiver(post_save, sender=Competition)
def populate_competition_judges_with_superusers(sender, instance, created, **kwargs):
    if created:
        superusers = CompetitionJudge.objects.filter(is_superuser=True)
        for user in superusers:
            instance.judges.add(user)
