from django.conf.urls import url, include

from .views import DashboardIndexView, DashboardManagementView

urlpatterns = [
    url(regex='^$',
        view=DashboardIndexView.as_view(),
        name='index'),
    url(regex='^management/$',
        view=DashboardManagementView.as_view(),
        name='management'),
    url(regex='^users/',
        view=include('odin.users.urls', namespace='users')
        ),
]
