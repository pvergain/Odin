from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from .models import Course, Teacher, Student
from .permissions import IsStudentOrTeacherInCoursePermission, IsTeacherInCoursePermission
from .mixins import CourseViewMixin
from .forms import TopicModelForm


class UserCoursesView(LoginRequiredMixin, TemplateView):
    template_name = 'education/courses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        select = ['description']
        prefetch = ['students', 'teachers']
        qs = Course.objects.select_related(*select).prefetch_related(*prefetch)

        context['user_is_teacher_for'] = []
        context['user_is_student_for'] = []

        teacher = user.downcast(Teacher)
        student = user.downcast(Student)

        if teacher:
            context['user_is_teacher_for'] = qs.filter(teachers=teacher)

        if student:
            context['user_is_student_for'] = qs.filter(students=student)

        return context


class CourseDetailView(CourseViewMixin,
                       LoginRequiredMixin,
                       IsStudentOrTeacherInCoursePermission,
                       TemplateView):

    template_name = 'education/course_detail.html'


class PublicCourseListView(ListView):

    template_name = 'education/all_courses.html'

    def get_queryset(self):
        return Course.objects.select_related('description')


class PublicCourseDetailView(DetailView):
    template_name = 'education/course_detail.html'

    def get_object(self):

        course_url = self.kwargs.get('course_slug')
        return get_object_or_404(Course, slug_url=course_url)


class AddTopicToCourseView(CourseViewMixin,
                           LoginRequiredMixin,
                           IsTeacherInCoursePermission,
                           FormView):
    template_name = 'education/add_topic.html'
    form_class = TopicModelForm
