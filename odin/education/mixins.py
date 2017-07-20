from typing import Callable, Dict

from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ValidationError
from django.contrib import messages

from .models import IncludedTask, Course


class CourseViewMixin:
    def dispatch(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')

        prefetch = (
            'students__profile',
            'teachers__profile',
            'topics__week',
            'topics__materials'
        )
        self.course = Course.objects.filter(id=course_id).prefetch_related(*prefetch)
        if not self.course.exists():
            return Http404

        self.course = self.course.first()

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


class CallServiceMixin:
    def call_service(self,
                     *,
                     service: Callable=None,
                     service_kwargs: Dict=None):
        try:
            return service(**service_kwargs)
        except ValidationError as e:
            messages.warning(request=self.request, message=str(e))
