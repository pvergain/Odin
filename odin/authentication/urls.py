from django.conf.urls import url
from rest_framework_jwt.views import refresh_jwt_token

from odin.authentication.apis import (
    LoginApi,
    UserDetailApi,
    LogoutApi,
    ForgotPasswordApi,
    ForgotPasswordSetApi,
)


urlpatterns = [
    url(
        regex='^login/$',
        view=LoginApi.as_view()
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
        view=ForgotPasswordApi.as_view()
    ),
    url(
        regex='^forgot-password/set/$',
        view=ForgotPasswordSetApi.as_view()
    ),
]
