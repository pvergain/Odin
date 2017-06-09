from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from .views import TestView


class CustomAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        """
        Required to bypass the automatic user population
        """
        pass
