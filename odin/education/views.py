from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Course, Teacher, Student
from .permissions import CourseDetailPermission
from .mixins import CourseViewMixin


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
                       CourseDetailPermission,
                       TemplateView):

    template_name = 'education/course_detail.html'
