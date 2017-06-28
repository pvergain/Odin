from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Course, Teacher, Student, Material, Topic
from .permissions import IsStudentOrTeacherInCoursePermission, IsTeacherInCoursePermission
from .mixins import CourseViewMixin, PublicViewContextMixin
from .forms import TopicModelForm, IncludedMaterialModelForm, IncludedMaterialFromExistingForm
from .services import create_topic, create_included_material


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


class PublicCourseListView(PublicViewContextMixin, ListView):

    template_name = 'education/all_courses.html'

    def get_queryset(self):
        return Course.objects.select_related('description')


class PublicCourseDetailView(PublicViewContextMixin, DetailView):
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

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def form_valid(self, form):
        create_topic(name=form.cleaned_data.get('name'),
                     week=form.cleaned_data.get('week'),
                     course=self.course)

        return super().form_valid(form)


class AddIncludedMaterialFromExistingView(CourseViewMixin,
                                          LoginRequiredMixin,
                                          IsTeacherInCoursePermission,
                                          ListView):
    template_name = 'education/existing_material_list.html'
    queryset = Material.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['topic_id'] = self.kwargs.get('topic_id')
        return context

    def post(self, request, *args, **kwargs):
        topic = get_object_or_404(Topic, id=self.kwargs.get('topic_id'))
        material = get_object_or_404(Material, identifier=request.POST.get('material_identifier'))

        data = {}
        data['topic'] = topic.id
        data['material'] = material.id

        form = IncludedMaterialFromExistingForm(data)

        if form.is_valid():
            create_included_material(existing_material=material, topic=topic)

        return redirect('dashboard:education:user-course-detail', course_id=self.course.id)


class AddNewIncludedMaterialView(CourseViewMixin,
                                 LoginRequiredMixin,
                                 IsTeacherInCoursePermission,
                                 FormView):
    template_name = 'education/add_material.html'
    form_class = IncludedMaterialModelForm

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_initial(self):
        self.initial = super().get_initial()
        self.initial['topic'] = self.kwargs.get('topic_id')
        return self.initial.copy()

    def get_form_kwargs(self):
        form_kwgs = super().get_form_kwargs()
        form_kwgs['course'] = self.course
        return form_kwgs

    def form_valid(self, form):
        create_included_material(identifier=form.cleaned_data.get('identifier'),
                                 url=form.cleaned_data.get('url'),
                                 topic=form.cleaned_data.get('topic'),
                                 content=form.cleaned_data.get('content'))

        return super().form_valid(form)
