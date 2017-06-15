from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from ..users.models import Profile


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'education/profile.html'

    def get_object(self, *args, **kwargs):
        return Profile.objects.get(user=self.request.user)
