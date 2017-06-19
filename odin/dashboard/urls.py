from django.conf.urls import url, include

from .views import (
    DashboardIndexView,
    DashboardManagementView,
    MakeStudentOrTeacherView,
    ManagementUserCreateView
)

urlpatterns = [
    url(regex='^$',
        view=DashboardIndexView.as_view(),
        name='index'),
    url(regex='^management/$',
        view=DashboardManagementView.as_view(),
        name='management'),
    url(regex='^users/',
        view=include('odin.users.urls', namespace='users')),
    url(regex='^management/promote/(?P<type>[A-Za-z]+)/(?P<id>[0-9]+)/$',
        view=MakeStudentOrTeacherView.as_view(),
        name='promote'),
    url(regex='^management/add-user/$',
        view=ManagementUserCreateView.as_view(),
        name='add-user')
]
