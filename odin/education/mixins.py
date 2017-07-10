from django.shortcuts import get_object_or_404

from .models import Course


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
