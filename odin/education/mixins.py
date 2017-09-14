from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages

from .models import IncludedTask, Course, IncludedTest


class CourseViewMixin:
    def dispatch(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        if not course_id:
            course_slug = self.kwargs.get('course_slug')

        prefetch = (
            'students__profile',
            'teachers__profile',
            'topics__week',
            'topics__materials',
            'topics__tasks',
            'weeks__lectures',

        )
        if course_id:
            self.course = Course.objects.filter(id=course_id).prefetch_related(*prefetch)
        else:
            self.course = Course.objects.filter(slug_url=course_slug).prefetch_related(*prefetch)
        if not self.course.exists():
            raise Http404

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
        if not self.request.is_ajax():
            return reverse_lazy('dashboard:education:student-solution-detail',
                                kwargs={'course_id': self.course.id,
                                        'task_id': self.kwargs.get('task_id'),
                                        'solution_id': self.solution_id})

        return reverse_lazy('dashboard:education:student-solution-detail-api',
                            kwargs={
                                'solution_id': self.solution_id
                            })


class TaskViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        return context


class HasTestMixin:
    def has_test(self):
        task = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        test = IncludedTest.objects.filter(task=task)
        if not test.exists():
            msg = 'This task has no tests added to it yet'
            messages.warning(request=self.request, message=msg)
            return redirect(reverse_lazy('dashboard:education:user-task-solutions',
                            kwargs={'course_id': self.course.id,
                                    'task_id': task.id}))
