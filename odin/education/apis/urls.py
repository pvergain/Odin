from django.conf.urls import url

from .views import MainView, SolutionStatusView

from .courses import StudentCoursesApi

urlpatterns = [
    url(
        regex='^(?P<task_id>[0-9]+)',
        view=MainView.as_view(),
        name='api_index_get'
    ),
    url(
        regex='^$',
        view=MainView.as_view(),
        name='api_index'
    ),
    url(
        regex='^solution/(?P<solution_id>[0-9]+)',
        view=SolutionStatusView.as_view(),
        name='solution_status'
    ),
    url(
        regex='^courses/$',
        view=StudentCoursesApi.as_view()
    ),
]
