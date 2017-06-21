from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Course
from .permissions import CourseDetailPermission


class UserCoursesView(LoginRequiredMixin, ListView):
    template_name = 'education/courses.html'

    def get_queryset(self, *args, **kwargs):
        return Course.objects.select_related('description').all().\
            prefetch_related('students', 'teachers')


class CourseDetailView(LoginRequiredMixin, CourseDetailPermission, DetailView):
    model = Course
    template_name = 'education/course_detail.html'
    slug_field = 'id'
    slug_url_kwarg = 'pk'
