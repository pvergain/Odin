from django.conf.urls import url
from rest_framework_jwt.views import refresh_jwt_token

from odin.education.apis.user import (
    LoginUnitedApi,
    UserDetailApi,
    LogoutApi,
    ForgotenPasswordApi,
    ForgotPasswordSetApi,
)


urlpatterns = [
    url(
        regex='^login/$',
        view=LoginUnitedApi.as_view()
    ),
    url(
        regex='^me/$',
        view=UserDetailApi.as_view()
    ),
    url(
        regex='^token-refresh/$',
        view=refresh_jwt_token
    ),
    url(
        regex='^logout/$',
        view=LogoutApi.as_view()
    ),
    url(
        regex='^forgot-password/reset/$',
        view=ForgotenPasswordApi.as_view()
    ),
    url(
        regex='^forgot-password/set/$',
        view=ForgotPasswordSetApi.as_view()
    ),
]
