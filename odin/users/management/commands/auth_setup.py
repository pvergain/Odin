from django.core.management.base import BaseCommand

from allauth.socialaccount.models import Site, SocialApp

import os


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        client_id = os.environ.get('GH_OAUTH_CLIENT_ID', None)
        secret_key = os.environ.get('GH_OAUTH_SECRET_KEY', None)

        if client_id is None or secret_key is None:
            print('Set up environment variables correctly')
            return
        site = Site.objects.first()
        site.domain = 'localhost:8000'
        social_app = SocialApp.objects.create(provider='github',
                                              name='OdinAuthTest',
                                              client_id=client_id,
                                              secret=secret_key)
        social_app.sites.add(site)
        social_app.save()
