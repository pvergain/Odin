from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from odin.common.mixins import ReadableFormErrorsMixin
from odin.management.permissions import DashboardManagementPermission
from odin.education.models import Course, IncludedTask

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
                tasks = IncludedTask.objects.get_tasks_for(course=course)
                task_count = tasks.count()
                solved_task_count = 0
                for task in tasks:
                    if task.solutions:
                        for solution in task.solutions.all():
                            if solution.status == 6 or solution.status == 2:
                                solved_task_count += 1

                if task_count > 0:
                    course_data.append((course, ((solved_task_count / task_count) * 100)))
                else:
                    course_data.append((course, 0))

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
    fields = ['full_name', 'description', 'full_image']
    success_url = reverse_lazy('dashboard:users:profile')
    template_name = 'users/edit_profile.html'

    def get_object(self, queryset=None):
        instance = get_object_or_404(Profile, user=self.request.user)
        return instance
