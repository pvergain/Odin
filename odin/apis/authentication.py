from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class JSONWebTokenAuthenticationMixin:
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated, )
