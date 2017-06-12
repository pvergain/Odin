from django.shortcuts import render
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'education/profile.html'

    def get_object(self, *args, **kwargs):
        return self.request.user
