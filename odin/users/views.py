from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from .models import Profile, BaseUser
from odin.management.permissions import DashboardManagementPermission


class PersonalProfileView(LoginRequiredMixin, DetailView):
    template_name = 'users/profile.html'

    def get_object(self, *args, **kwargs):
        return Profile.objects.get(user=self.request.user)


class UserProfileView(LoginRequiredMixin, DashboardManagementPermission, DetailView):
    template_name = 'users/profile.html'

    def get_object(self, *args, **kwargs):
        user_email = self.kwargs.get('user_email')
        user_instance = get_object_or_404(BaseUser, email=user_email)
        return Profile.objects.get(user=user_instance)
