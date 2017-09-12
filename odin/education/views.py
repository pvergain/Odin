import json

from rest_framework import generics

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
from django.http import JsonResponse

from odin.common.utils import transfer_POST_data_to_dict
from odin.common.mixins import CallServiceMixin, ReadableFormErrorsMixin
from odin.management.permissions import DashboardManagementPermission
from odin.grading.services import start_grader_communication

from .models import (
    Course,
    Teacher,
    Student,
    Material,
    Task,
    IncludedTask,
    Solution,
    IncludedTest,
    IncludedMaterial
)
from .permissions import (
    IsStudentOrTeacherInCoursePermission,
    IsTeacherInCoursePermission,
    IsStudentInCoursePermission,
    IsStudentOrTeacherInCourseAPIPermission
)
from .mixins import (
    CourseViewMixin,
    PublicViewContextMixin,
    SubmitSolutionMixin,
    TaskViewMixin,
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
    create_non_gradable_solution,
    calculate_student_valid_solutions_for_course
)
from .serializers import TopicSerializer, SolutionSerializer


class UserCoursesView(LoginRequiredMixin, TemplateView):
    template_name = 'education/courses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        prefetch = ['students', 'teachers', 'weeks']
        qs = Course.objects.prefetch_related(*prefetch)

        context['user_is_teacher_for'] = []
        context['user_is_student_for'] = []

        teacher = user.downcast(Teacher)
        student = user.downcast(Student)

        if teacher:
            context['user_is_teacher_for'] = qs.filter(teachers=teacher)

        if student:
            context['user_is_student_for'] = qs.filter(students=student)

        return context


class CourseDetailView(LoginRequiredMixin,
                       CourseViewMixin,
                       IsStudentOrTeacherInCoursePermission,
                       TemplateView):

    template_name = 'education/course_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_queryset = self.course.topics.prefetch_related('tasks__solutions', 'materials', 'tasks__test__language')
        topics = TopicSerializer(topic_queryset, many=True)
        course_topics = {}
        course_topics['data'] = topics.data
        context['course_topics'] = json.dumps(course_topics)
        if self.request.user.is_student():
            student = self.request.user.student
            context['tasks_ratio'] = calculate_student_valid_solutions_for_course(student=student, course=self.course)
        return context


class PublicCourseListView(PublicViewContextMixin, ListView):

    template_name = 'education/all_courses.html'

    def get_queryset(self):
        return Course.objects.filter(public=True).select_related('description').prefetch_related('weeks')


class PublicCourseDetailView(CourseViewMixin, PublicViewContextMixin, DetailView):
    template_name = 'education/course_detail.html'

    def get_object(self):

        course_url = self.kwargs.get('course_slug')

        return get_object_or_404(Course, slug_url=course_url)


class AddTopicToCourseView(LoginRequiredMixin,
                           CourseViewMixin,
                           CallServiceMixin,
                           ReadableFormErrorsMixin,
                           IsTeacherInCoursePermission,
                           FormView):
    template_name = 'education/add_topic.html'
    form_class = TopicModelForm

    def get_service(self):
        return create_topic

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

        self.call_service(service_kwargs=create_topic_kwargs)

        return super().form_valid(form)


class AddIncludedMaterialFromExistingView(LoginRequiredMixin,
                                          CourseViewMixin,
                                          CallServiceMixin,
                                          ReadableFormErrorsMixin,
                                          IsTeacherInCoursePermission,
                                          FormView):
    template_name = 'education/existing_material_list.html'
    form_class = IncludedMaterialFromExistingForm

    def get_service(self):
        return create_included_material

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

        data = transfer_POST_data_to_dict(self.request.POST)
        data['topic'] = self.kwargs.get('topic_id')
        form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        data = {}
        data['existing_material'] = form.cleaned_data.get('material')
        data['topic'] = form.cleaned_data.get('topic')

        self.call_service(service_kwargs=data)

        return super().form_valid(form)


class ExistingMaterialListView(LoginRequiredMixin,
                               CourseViewMixin,
                               IsTeacherInCoursePermission,
                               ListView):
    template_name = 'education/existing_material_list.html'
    queryset = Material.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['topic_id'] = self.kwargs.get('topic_id')

        return context


class AddNewIncludedMaterialView(LoginRequiredMixin,
                                 CourseViewMixin,
                                 CallServiceMixin,
                                 ReadableFormErrorsMixin,
                                 IsTeacherInCoursePermission,
                                 FormView):
    template_name = 'education/add_material.html'
    form_class = IncludedMaterialModelForm

    def get_service(self):
        return create_included_material

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

        self.call_service(service_kwargs=create_included_material_kwargs)

        return super().form_valid(form)


class ExistingTasksView(LoginRequiredMixin,
                        CourseViewMixin,
                        IsTeacherInCoursePermission,
                        FormView):
    template_name = 'education/existing_task_list.html'
    form_class = IncludedTaskFromExistingForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['course'] = self.course

        data = transfer_POST_data_to_dict(self.request.POST)
        data['topic'] = self.kwargs.get('topic_id')
        form_kwargs['data'] = data

        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_list'] = Task.objects.all()
        context['topic_id'] = self.kwargs.get('topic_id')

        return context


class AddNewIncludedTaskView(LoginRequiredMixin,
                             CourseViewMixin,
                             CallServiceMixin,
                             ReadableFormErrorsMixin,
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

        task = self.call_service(service=create_included_task, service_kwargs=create_included_task_kwargs)
        if task.gradable:
            create_test_kwargs = {
                'task': task,
                'language': form.cleaned_data.get('language'),
                'code': form.cleaned_data.get('code') if form.cleaned_data.get('code') != '' else None,
                'file': form.cleaned_data.get('file')
            }

            self.call_service(service=create_test_for_task, service_kwargs=create_test_kwargs)

        return super().form_valid(form)


class AddIncludedTaskFromExistingView(LoginRequiredMixin,
                                      CourseViewMixin,
                                      CallServiceMixin,
                                      ReadableFormErrorsMixin,
                                      IsTeacherInCoursePermission,
                                      FormView):
    template_name = 'education/existing_task_list.html'
    form_class = IncludedTaskFromExistingForm

    def get_service(self):
        return create_included_task

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['topic_id'] = self.kwargs.get('topic_id')
        context['task_list'] = Task.objects.all()

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['topic'] = self.kwargs.get('topic_id')
            form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        create_included_task_kwargs = {
            'existing_task': form.cleaned_data.get('task'),
            'topic': form.cleaned_data.get('topic')
        }

        self.call_service(service_kwargs=create_included_task_kwargs)

        return super().form_valid(form)


class TaskDetailView(LoginRequiredMixin,
                     TaskViewMixin,
                     DetailView):
    model = IncludedTask
    pk_url_kwarg = 'task_id'
    template_name = 'education/task_detail.html'


class MaterialDetailView(LoginRequiredMixin,
                         DetailView):
    model = IncludedMaterial
    pk_url_kwarg = 'material_id'
    template_name = 'education/material_detail.html'


class EditTaskView(LoginRequiredMixin,
                   ReadableFormErrorsMixin,
                   DashboardManagementPermission,
                   UpdateView):

    model = Task
    fields = ('name', 'description', 'gradable')
    pk_url_kwarg = 'task_id'
    template_name = 'education/edit_task.html'

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-courses')


class EditIncludedTaskView(LoginRequiredMixin,
                           CourseViewMixin,
                           ReadableFormErrorsMixin,
                           IsTeacherInCoursePermission,
                           UpdateView):

    model = IncludedTask
    form_class = IncludedTaskModelForm
    pk_url_kwarg = 'task_id'
    template_name = 'education/edit_included_task.html'

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


class AddSourceCodeTestToTaskView(LoginRequiredMixin,
                                  CourseViewMixin,
                                  CallServiceMixin,
                                  ReadableFormErrorsMixin,
                                  IsTeacherInCoursePermission,
                                  FormView):

    form_class = SourceCodeTestForm
    template_name = 'education/add_source_test.html'

    def get_service(self):
        return create_test_for_task

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['task'] = self.kwargs.get('task_id')

            form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        self.call_service(service_kwargs=form.cleaned_data)

        return super().form_valid(form)


class AddBinaryFileTestToTaskView(LoginRequiredMixin,
                                  CourseViewMixin,
                                  CallServiceMixin,
                                  ReadableFormErrorsMixin,
                                  IsTeacherInCoursePermission,
                                  FormView):

    form_class = BinaryFileTestForm
    template_name = 'education/add_binary_test.html'

    def get_service(self):
        return create_test_for_task

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['task'] = self.kwargs.get('task_id')

            form_kwargs['data'] = data

        return form_kwargs

    def form_valid(self, form):
        self.call_service(service_kwargs=form.cleaned_data)

        return super().form_valid(form)


class EditIncludedTestView(LoginRequiredMixin,
                           CourseViewMixin,
                           ReadableFormErrorsMixin,
                           IsTeacherInCoursePermission,
                           UpdateView):
    model = IncludedTest
    template_name = 'education/edit_included_test.html'

    def get_object(self):
        task = IncludedTask.objects.get(id=self.kwargs.get('task_id'))

        return task.test

    def get_form_class(self):
        if self.object.is_source():
            return SourceCodeTestForm

        return BinaryFileTestForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            data = transfer_POST_data_to_dict(self.request.POST)
            data['task'] = self.kwargs.get('task_id')

            form_kwargs['data'] = data

        return form_kwargs

    def get_success_url(self):
        return reverse_lazy('dashboard:education:user-course-detail',
                            kwargs={'course_id': self.course.id})


class StudentSolutionListView(LoginRequiredMixin,
                              CourseViewMixin,
                              TaskViewMixin,
                              IsStudentInCoursePermission,
                              ListView):
    template_name = 'education/student_solution_list.html'

    def get_queryset(self):
        user = self.request.user
        task = get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))

        return Solution.objects.get_solutions_for(user.student, task)


class StudentSolutionDetailView(LoginRequiredMixin,
                                CourseViewMixin,
                                TaskViewMixin,
                                IsStudentOrTeacherInCoursePermission,
                                DetailView):
    model = Solution
    pk_url_kwarg = 'solution_id'
    template_name = 'education/student_solution_detail.html'


class SubmitGradableSolutionView(LoginRequiredMixin,
                                 CourseViewMixin,
                                 TaskViewMixin,
                                 CallServiceMixin,
                                 ReadableFormErrorsMixin,
                                 SubmitSolutionMixin,
                                 HasTestMixin,
                                 IsStudentInCoursePermission,
                                 FormView):
    form_class = SubmitGradableSolutionForm

    def get_service(self):
        return create_gradable_solution

    def get(self, request, *args, **kwargs):
        res = self.has_test()

        return res or super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        res = self.has_test()

        return res or super().post(request, *args, **kwargs)

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

        solution = self.call_service(service_kwargs=create_gradable_solution_kwargs)
        if solution:
            self.solution_id = solution.id
            start_grader_communication(solution.id)

        return super().form_valid(form)

    def form_invalid(self, form):
        if not self.request.is_ajax():
            return super().form_invalid(form)
        else:
            data = {
                'errors': form.errors
            }
            return JsonResponse(data=data)


class SubmitNonGradableSolutionView(LoginRequiredMixin,
                                    CourseViewMixin,
                                    TaskViewMixin,
                                    CallServiceMixin,
                                    ReadableFormErrorsMixin,
                                    SubmitSolutionMixin,
                                    IsStudentInCoursePermission,
                                    FormView):
    form_class = SubmitNonGradableSolutionForm

    def get_service(self):
        return create_non_gradable_solution

    def form_valid(self, form):
        create_non_gradable_solution_kwargs = {
            'student': self.request.user.student,
            'task': get_object_or_404(IncludedTask, id=self.kwargs.get('task_id'))
        }
        create_non_gradable_solution_kwargs.update(form.cleaned_data)

        solution = self.call_service(service_kwargs=create_non_gradable_solution_kwargs)
        if solution:
            self.solution_id = solution.id

        return super().form_valid(form)

    def form_invalid(self, form):
        if not self.request.is_ajax():
            return super().form_invalid(form)
        else:
            data = {
                'errors': form.errors
            }
            return JsonResponse(data=data)


class AllStudentsSolutionsView(LoginRequiredMixin,
                               CourseViewMixin,
                               TaskViewMixin,
                               IsTeacherInCoursePermission,
                               ListView):
    template_name = "education/all_students_solutions.html"

    def get_queryset(self):
        return self.course.students.select_related('profile').prefetch_related('solutions__task').all()


class SolutionDetailAPIView(generics.RetrieveAPIView):
    serializer_class = SolutionSerializer
    permission_classes = (IsStudentOrTeacherInCourseAPIPermission, )
    queryset = Solution.objects.all()
    lookup_url_kwarg = 'solution_id'
