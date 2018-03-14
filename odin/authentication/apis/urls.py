from django.conf.urls import url
from rest_framework_jwt.views import refresh_jwt_token

from odin.education.apis.user import LoginUnitedApi


urlpatterns = [
    url(
        regex='^login/$',
        view=LoginUnitedApi.as_view()
    ),
    url(
        regex='^token-refresh/',
        view=refresh_jwt_token
    ),
]
