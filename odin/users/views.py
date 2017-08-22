from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from odin.common.mixins import ReadableFormErrorsMixin, CallServiceMixin
from odin.management.permissions import DashboardManagementPermission

from .models import Profile, BaseUser
from .services import update_user_profile


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


class EditProfileView(LoginRequiredMixin,
                      ReadableFormErrorsMixin,
                      CallServiceMixin,
                      UpdateView):
    model = Profile
    fields = ['full_name', 'description', 'avatar', 'cropping', 'mac']

    success_url = reverse_lazy('dashboard:users:profile')
    template_name = 'users/edit_profile.html'

    def get_service(self):
        return update_user_profile

    def get_object(self, queryset=None):
        instance = get_object_or_404(Profile, user=self.request.user)
        return instance

    def form_valid(self, form):
        user = BaseUser.objects.filter(profile=self.get_object())
        if user.exists():
            user = user.first()
            service_kwargs = {
                'user': user,
                'data': form.cleaned_data
            }
            self.call_service(service_kwargs=service_kwargs)

        return super().form_valid(form)
