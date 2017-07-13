from .models import Course, IncludedTask

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


class CourseViewMixin:
    def dispatch(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')

        prefetch = (
            'students__profile',
            'teachers__profile',
            'topics__week',
            'topics__materials'
        )
        self.course = Course.objects.filter(id=course_id).prefetch_related(*prefetch).first()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['course'] = self.course

        return context


class PublicViewContextMixin:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['public_page'] = True
        return context


class SubmitSolutionMixin:
    template_name = 'education/submit_solution.html'

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})


class TaskViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        return context
