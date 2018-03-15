import datetime

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.settings import api_settings

from .serializers import UserSerializer, ProfileSerializer

from .permissions import StudentCourseAuthenticationMixin

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class LoginUnitedApi(ObtainJSONWebToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            user_data = UserSerializer(instance=user).data
            profile_data = ProfileSerializer(instance=user.profile).data
            full_data = {**user_data, **profile_data}
            response_data = jwt_response_payload_handler(token, user, request)
            response_data.update({'me': full_data})
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


class UserDetailApi(StudentCourseAuthenticationMixin, APIView):

    def get(self, request):
        user = self.request.user
        user_data = UserSerializer(instance=user).data
        profile_data = ProfileSerializer(instance=user.profile).data
        full_data = {**user_data, **profile_data}

        return Response(full_data)
