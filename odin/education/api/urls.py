from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token


from .views import MainView, SolutionStatusView

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
        regex='^token-auth/',
        view=obtain_jwt_token
    ),
    url(
        regex='^token-refresh/',
        view=refresh_jwt_token
    ),
]
