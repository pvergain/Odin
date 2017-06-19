from django.conf.urls import url

from .views import MakeStudentOrTeacherView, ManagementUserCreateView, DashboardManagementView

urlpatterns = [
    url(regex='^$',
        view=DashboardManagementView.as_view(),
        name='management_index'),
    url(regex='^promote/(?P<type>[A-Za-z]+)/(?P<id>[0-9]+)/$',
        view=MakeStudentOrTeacherView.as_view(),
        name='promote'),
    url(regex='^add-user/$',
        view=ManagementUserCreateView.as_view(),
        name='add-user'),
]
