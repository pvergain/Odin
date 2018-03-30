from django.urls import reverse_lazy
from django.apps import apps
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from django.core.exceptions import ValidationError


class CourseViewMixin:
    def dispatch(self, request, *args, **kwargs):
        Course = apps.get_model('education.Course')
        course_id = self.kwargs.get('course_id')
        if not course_id:
            course_slug = self.kwargs.get('course_slug')

        prefetch = (
            'students__profile',
            'teachers__profile',
            'week',
            'materials',
            'tasks__solutions',
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
        IncludedTask = apps.get_model('education.IncludedTask')
        context = super().get_context_data(**kwargs)
        context['task'] = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        return context


class HasTestMixin:
    def has_test(self):
        IncludedTask = apps.get_model('education.IncludedTask')
        IncludedTest = apps.get_model('education.IncludedTest')
        task = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        test = IncludedTest.objects.filter(task=task)
        if not test.exists():
            msg = 'This task has no tests added to it yet'
            messages.warning(request=self.request, message=msg)
            return redirect(reverse_lazy('dashboard:education:user-task-solutions',
                            kwargs={'course_id': self.course.id,
                                    'task_id': task.id}))


class TestModelMixin:
    def is_source(self):
        return bool(getattr(self, 'code', None))

    def is_binary(self):
        return bool(getattr(self, 'file', None))

    def test_mode(self):
        if self.is_binary:
            return 'binary'
        return 'plain'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        if not self.task.gradable:
            raise ValidationError("Can not add tests to a non-gradable task")

        if self.code is None and str(self.file) is '':
            raise ValidationError("A binary file or source code must be provided!")

        if self.code is not None and str(self.file) is not '':
            raise ValidationError("Either a binary file or source code must be provided")
