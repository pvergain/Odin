from django.shortcuts import render
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin


class SampleProfileView(LoginRequiredMixin, DetailView):
    template_name = 'education/sample_profile.html'

    def get_object(self, *args, **kwargs):
        return self.request.user
