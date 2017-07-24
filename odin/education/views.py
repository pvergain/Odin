from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    FormView,
    UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from odin.management.permissions import DashboardManagementPermission

from .models import Course, Teacher, Student, Material, Task, IncludedTask, Solution
from .permissions import (
    IsStudentOrTeacherInCoursePermission,
    IsTeacherInCoursePermission,
    IsStudentInCoursePermission,
)
from .mixins import (
    CourseViewMixin,
    PublicViewContextMixin,
    SubmitSolutionMixin,
    TaskViewMixin,
    CallServiceMixin,
    HasTestMixin,
)
from .forms import (
    TopicModelForm,
    IncludedMaterialModelForm,
    IncludedMaterialFromExistingForm,
    IncludedTaskModelForm,
    IncludedTaskFromExistingForm,
    SourceCodeTestForm,
    BinaryFileTestForm,
    SubmitGradableSolutionForm,
    SubmitNonGradableSolutionForm,
)
from .services import (
    create_topic,
    create_included_material,
    create_included_task,
    create_test_for_task,
    create_gradable_solution,
    create_non_gradable_solution
)


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
        return Course.objects.filter(public=True).select_related('description')


class PublicCourseDetailView(PublicViewContextMixin, DetailView):
    template_name = 'education/course_detail.html'

    def get_object(self):

        course_url = self.kwargs.get('course_slug')
        return get_object_or_404(Course, slug_url=course_url)


class AddTopicToCourseView(CourseViewMixin,
                           CallServiceMixin,
                           LoginRequiredMixin,
                           IsTeacherInCoursePermission,
                           FormView):
    template_name = 'education/add_topic.html'
    form_class = TopicModelForm

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course
        return form_kwargs

    def form_valid(self, form):

        create_topic_kwargs = {
            'name': form.cleaned_data.get('name'),
            'week': form.cleaned_data.get('week'),
            'course': self.course
        }

        self.call_service(service=create_topic, service_kwargs=create_topic_kwargs)
        return super().form_valid(form)


class AddIncludedMaterialFromExistingView(CourseViewMixin,
                                          CallServiceMixin,
                                          LoginRequiredMixin,
                                          IsTeacherInCoursePermission,
                                          FormView):
    template_name = 'education/existing_material_list.html'
    form_class = IncludedMaterialFromExistingForm

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['topic_id'] = self.kwargs.get('topic_id')

        context['material_list'] = Material.objects.all()

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        data = {}
        data['topic'] = self.kwargs.get('topic_id')
        data['material'] = self.request.POST.get('material')
        form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        data = {}
        data['existing_material'] = form.cleaned_data.get('material')
        data['topic'] = form.cleaned_data.get('topic')

        self.call_service(service=create_included_material, service_kwargs=data)

        return super().form_valid(form)


class ExistingMaterialListView(CourseViewMixin,
                               LoginRequiredMixin,
                               IsTeacherInCoursePermission,
                               ListView):
    template_name = 'education/existing_material_list.html'
    queryset = Material.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['topic_id'] = self.kwargs.get('topic_id')
        return context


class AddNewIncludedMaterialView(CourseViewMixin,
                                 CallServiceMixin,
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
        return self.initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course
        return form_kwargs

    def form_valid(self, form):
        create_included_material_kwargs = {
            'identifier': form.cleaned_data.get('identifier'),
            'url': form.cleaned_data.get('url'),
            'topic': form.cleaned_data.get('topic'),
            'content': form.cleaned_data.get('content')
        }

        self.call_service(service=create_included_material, service_kwargs=create_included_material_kwargs)

        return super().form_valid(form)


class ExistingTasksView(CourseViewMixin,
                        LoginRequiredMixin,
                        IsTeacherInCoursePermission,
                        FormView):
    template_name = 'education/existing_task_list.html'
    form_class = IncludedTaskFromExistingForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_list'] = Task.objects.all()
        return context


class AddNewIncludedTaskView(CourseViewMixin,
                             CallServiceMixin,
                             LoginRequiredMixin,
                             IsTeacherInCoursePermission,
                             FormView):
    template_name = 'education/add_task.html'
    form_class = IncludedTaskModelForm

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_initial(self):
        self.initial = super().get_initial()
        self.initial['topic'] = self.kwargs.get('topic_id')
        return self.initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course
        return form_kwargs

    def form_valid(self, form):
        create_included_task_kwargs = {
            'name': form.cleaned_data.get('name'),
            'description': form.cleaned_data.get('description'),
            'gradable': form.cleaned_data.get('gradable'),
            'topic': form.cleaned_data.get('topic')
        }

        self.call_service(service=create_included_task, service_kwargs=create_included_task_kwargs)

        return super().form_valid(form)


class AddIncludedTaskFromExistingView(CourseViewMixin,
                                      CallServiceMixin,
                                      LoginRequiredMixin,
                                      IsTeacherInCoursePermission,
                                      FormView):
    template_name = 'education/existing_task_list.html'
    form_class = IncludedTaskFromExistingForm

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['task_list'] = Task.objects.all()

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        data = {}
        data['topic'] = self.request.POST.get('topic')
        data['task'] = self.request.POST.get('task')
        form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        create_included_task_kwargs = {
            'existing_task': form.cleaned_data.get('task'),
            'topic': form.cleaned_data.get('topic')
        }

        self.call_service(service=create_included_task, service_kwargs=create_included_task_kwargs)

        return super().form_valid(form)


class TaskDetailView(TaskViewMixin,
                     LoginRequiredMixin,
                     DetailView):
    model = IncludedTask
    pk_url_kwarg = 'task_id'
    template_name = 'education/task_detail.html'


class EditTaskView(LoginRequiredMixin,
                   DashboardManagementPermission,
                   UpdateView):

    model = Task
    fields = ('name', 'description', 'gradable')
    pk_url_kwarg = 'task_id'
    template_name = "education/edit_task.html"

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-courses')


class EditIncludedTaskView(CourseViewMixin,
                           LoginRequiredMixin,
                           IsTeacherInCoursePermission,
                           UpdateView):

    model = IncludedTask
    form_class = IncludedTaskModelForm
    pk_url_kwarg = 'task_id'
    template_name = "education/edit_included_task.html"

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course
        return form_kwargs

    def get_initial(self):
        instance = self.get_object()
        self.initial = super().get_initial()
        self.initial['topic'] = instance.topic.id
        return self.initial

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})


class AddSourceCodeTestToTaskView(CourseViewMixin,
                                  CallServiceMixin,
                                  LoginRequiredMixin,
                                  IsTeacherInCoursePermission,
                                  FormView):

    form_class = SourceCodeTestForm
    template_name = 'education/add_source_test.html'

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = {}
            data['task'] = self.kwargs.get('task_id')
            data['language'] = self.request.POST.get('language')
            data['code'] = self.request.POST.get('code')

            form_kwargs['data'] = data
        return form_kwargs

    def form_valid(self, form):
        self.call_service(service=create_test_for_task, service_kwargs=form.cleaned_data)
        return super().form_valid(form)


class AddBinaryFileTestToTaskView(CourseViewMixin,
                                  CallServiceMixin,
                                  LoginRequiredMixin,
                                  IsTeacherInCoursePermission,
                                  FormView):

    form_class = BinaryFileTestForm
    template_name = 'education/add_binary_test.html'

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = {}
            data['task'] = self.kwargs.get('task_id')
            data['language'] = self.request.POST.get('language')
            data['file'] = self.request.FILES.get('file')

            form_kwargs['data'] = data
        return form_kwargs

    def form_valid(self, form):
        self.call_service(service=create_test_for_task, service_kwargs=form.cleaned_data)
        return super().form_valid(form)


class StudentSolutionListView(CourseViewMixin,
                              TaskViewMixin,
                              LoginRequiredMixin,
                              IsStudentInCoursePermission,
                              ListView):
    template_name = 'education/student_solution_list.html'

    def get_queryset(self):
        user = self.request.user
        task = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        return Solution.objects.get_solutions_for(user.student, task)


class StudentSolutionDetailView(CourseViewMixin,
                                TaskViewMixin,
                                LoginRequiredMixin,
                                IsStudentInCoursePermission,
                                DetailView):
    model = Solution
    pk_url_kwarg = 'solution_id'
    template_name = 'education/student_solution_detail.html'


class EditStudentSolutionView(CourseViewMixin,
                              TaskViewMixin,
                              LoginRequiredMixin,
                              IsStudentInCoursePermission,
                              UpdateView):
    model = Solution
    fields = ('code', 'file', 'url')
    pk_url_kwarg = 'solution_id'
    template_name = 'education/edit_student_solution.html'

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})


class SubmitGradableSolutionView(CourseViewMixin,
                                 TaskViewMixin,
                                 CallServiceMixin,
                                 SubmitSolutionMixin,
                                 HasTestMixin,
                                 LoginRequiredMixin,
                                 IsStudentInCoursePermission,
                                 FormView):
    form_class = SubmitGradableSolutionForm

    def get(self, *args, **kwargs):
        res = self.has_test()
        return res or super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        res = self.has_test()
        return res or super().post(*args, **kwargs)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        task = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        test = task.test

        form_kwargs['is_test_source'] = test.is_source()
        return form_kwargs

    def form_valid(self, form):
        create_gradable_solution_kwargs = {
            'student': self.request.user.student,
            'task': get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        }
        create_gradable_solution_kwargs.update(form.cleaned_data)

        self.call_service(service=create_gradable_solution, service_kwargs=create_gradable_solution_kwargs)
        return super().form_valid(form)


class SubmitNonGradableSolutionView(CourseViewMixin,
                                    TaskViewMixin,
                                    CallServiceMixin,
                                    SubmitSolutionMixin,
                                    LoginRequiredMixin,
                                    IsStudentInCoursePermission,
                                    FormView):
    form_class = SubmitNonGradableSolutionForm

    def form_valid(self, form):
        create_non_gradable_solution_kwargs = {
            'student': self.request.user.student,
            'task': get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        }
        create_non_gradable_solution_kwargs.update(form.cleaned_data)

        self.call_service(service=create_non_gradable_solution, service_kwargs=create_non_gradable_solution_kwargs)
        return super().form_valid(form)
