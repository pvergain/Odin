import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.views import JSONWebTokenAPIView, JSONWebTokenSerializer

from .serializers import UserSerializer

from rest_framework_jwt.settings import api_settings

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class LoginUnitedApi(JSONWebTokenAPIView):
    serializer_class = JSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            user_data = UserSerializer(instance=user).data
            response_data = jwt_response_payload_handler(token, user, request)
            response_data.update({'me': user_data})
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
