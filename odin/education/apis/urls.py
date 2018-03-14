from django.conf.urls import url

from .courses import StudentCoursesApi, CourseDetailApi

from .tasks import TaskDetailApi

from .solutions import SolutionSubmitAPIView

urlpatterns = [
    url(
        regex='^solution/$',
        view=SolutionSubmitAPIView.as_view(),
    ),
    url(
        regex='^solution/(?P<solution_id>[0-9]+)$',
        view=SolutionSubmitAPIView.as_view(),
    ),
    url(
        regex='^courses/$',
        view=StudentCoursesApi.as_view()
    ),
    url(
        regex='^courses/(?P<course_id>[0-9]+)/$',
        view=CourseDetailApi.as_view()
    ),
    url(
        regex='^task/(?P<task_id>[0-9]+)/$',
        view=TaskDetailApi.as_view()
    ),
]
