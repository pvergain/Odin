from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from odin.education.apis.user import UserDetailApi


urlpatterns = [
    url(
        regex='^login/$',
        view=obtain_jwt_token
    ),
    url(
        regex='^token-refresh/',
        view=refresh_jwt_token
    ),
    url(
        regex='^me/$',
        view=UserDetailApi.as_view()
    ),
]
