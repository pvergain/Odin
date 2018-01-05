from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from odin.common.mixins import ReadableFormErrorsMixin
from odin.management.permissions import DashboardManagementPermission
from odin.education.models import Course
from odin.education.services import calculate_student_valid_solutions_for_course

from .models import Profile, BaseUser


class PersonalProfileView(LoginRequiredMixin, DetailView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        course_data = []
        if user.is_student():
            student = user.student
            courses = Course.objects.filter(students__in=[student])
            for course in courses:
                course_data.append((course, calculate_student_valid_solutions_for_course(
                    course=course,
                    student=student)))

        context['course_data'] = course_data

        return context

    def get_object(self, *args, **kwargs):
        return Profile.objects.get(user=self.request.user)


class UserProfileView(LoginRequiredMixin, DashboardManagementPermission, DetailView):
    template_name = 'users/profile.html'

    def get_object(self, *args, **kwargs):
        user_email = self.kwargs.get('user_email')
        user_instance = get_object_or_404(BaseUser, email=user_email)
        return Profile.objects.get(user=user_instance)


class EditProfileView(LoginRequiredMixin, ReadableFormErrorsMixin, UpdateView):
    model = Profile
    fields = ['full_name', 'description', 'full_image', 'skype']
    success_url = reverse_lazy('dashboard:users:profile')
    template_name = 'users/edit_profile.html'

    def get_object(self, queryset=None):
        instance = get_object_or_404(Profile, user=self.request.user)
        return instance
