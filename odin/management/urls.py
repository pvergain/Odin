from django.conf.urls import url

from .views import (PromoteUserToStudentView,
                    PromoteUserToTeacherView,
                    DashboardManagementView,
                    CreateUserView,
                    CreateStudentView,
                    CreateTeacherView)

urlpatterns = [
    url(regex='^$',
        view=DashboardManagementView.as_view(),
        name='management_index'),
    url(regex='^promote/student/(?P<id>[0-9]+)/$',
        view=PromoteUserToStudentView.as_view(),
        name='promote-to-student'),
    url(regex='^promote/teacher/(?P<id>[0-9]+)/$',
        view=PromoteUserToTeacherView.as_view(),
        name='promote-to-teacher'),
    url(regex='^add-student/$',
        view=CreateStudentView.as_view(),
        name='add-student'),
    url(regex='^add-user/$',
        view=CreateUserView.as_view(),
        name='add-user'),
    url(regex='^add-teacher/$',
        view=CreateTeacherView.as_view(),
        name='add-teacher'),
]
