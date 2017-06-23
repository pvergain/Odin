from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

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


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ['full_name', 'description', 'avatar', 'cropping']
    success_url = reverse_lazy('dashboard:users:profile')
    template_name = 'users/edit_profile.html'

    def get_object(self, queryset=None):
        instance = get_object_or_404(Profile, user=self.request.user)
        return instance
