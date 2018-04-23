from django.conf.urls import url
from rest_framework_jwt.views import refresh_jwt_token

from odin.authentication.apis import (
    LoginApi,
    UserDetailApi,
    LogoutApi,
    ForgotPasswordApi,
    ForgotPasswordSetApi,
    ChangePasswordApi,
    SignS3Api
)


urlpatterns = [
    url(
        regex='^login/$',
        view=LoginApi.as_view(),
        name='login'
    ),
    url(
        regex='^me/$',
        view=UserDetailApi.as_view(),
        name='user-detail'
    ),
    url(
        regex='^token-refresh/$',
        view=refresh_jwt_token
    ),
    url(
        regex='^logout/$',
        view=LogoutApi.as_view(),
        name='logout'
    ),
    url(
        regex='^forgot-password/reset/$',
        view=ForgotPasswordApi.as_view(),
        name='forgot-password-reset'
    ),
    url(
        regex='^forgot-password/set/$',
        view=ForgotPasswordSetApi.as_view(),
        name='forgot-password-set'
    ),
    url(
        regex='^change-password/$',
        view=ChangePasswordApi.as_view(),
        name='change-password'
    ),
    url(
        regex='^sign-s3/$',
        view=SignS3Api.as_view(),
        name='sign-s3'
    ),
]
