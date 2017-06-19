from django.conf.urls import url, include

from .views import DashboardIndexView

urlpatterns = [
    url(regex='^$',
        view=DashboardIndexView.as_view(),
        name='index'),
    url(regex='^management/',
        view=include('odin.management.urls', namespace='management')),
    url(regex='^users/',
        view=include('odin.users.urls', namespace='users')
        ),
]
