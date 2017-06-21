from django.core.management.base import BaseCommand
from django.conf import settings

from allauth.socialaccount.models import Site, SocialApp


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        client_id = settings.GH_OAUTH_CLIENT_ID
        secret_key = settings.GH_OAUTH_SECRET_KEY

        if client_id is None or secret_key is None:
            print('Set up environment variables correctly')
            return
        site = Site.objects.first()

        social_app = SocialApp.objects.create(provider='github',
                                              name='OdinAuthTest',
                                              client_id=client_id,
                                              secret=secret_key)
        social_app.sites.add(site)
        social_app.save()
