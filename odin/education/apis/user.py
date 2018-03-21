from rest_framework import status
from rest_framework import serializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.settings import api_settings

from django.utils import timezone

from odin.emails.services import send_mail

from odin.users.models import BaseUser, PasswordReset
from odin.apis.mixins import ServiceExceptionHandlerMixin

from .serializers import UserSerializer, ProfileSerializer, PasswordResetSerializer
from .permissions import StudentCourseAuthenticationMixin

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class LoginUnitedApi(ObtainJSONWebToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = data.get('user')
        token = data.get('token')
        user_data = UserSerializer(instance=user).data
        profile_data = ProfileSerializer(instance=user.profile).data
        full_data = {**user_data, **profile_data}

        response_data = jwt_response_payload_handler(token, user, request)
        response_data.update({'me': full_data})

        return Response(response_data)


class UserDetailApi(StudentCourseAuthenticationMixin, APIView):

    def get(self, request):
        user = self.request.user
        user_data = UserSerializer(instance=user).data
        profile_data = ProfileSerializer(instance=user.profile).data
        full_data = {**user_data, **profile_data}

        return Response(full_data)


class LogoutApi(StudentCourseAuthenticationMixin, APIView):
    def post(self, request):
        user = self.request.user
        user.rotate_secret_key()
        return Response(status=status.HTTP_202_ACCEPTED)


class ForgotenPasswordApi(ServiceExceptionHandlerMixin, APIView):
    class Serializer(serializers.Serializer):
        email = serializers.EmailField()

    def post(self, request):
        serializer = self.Serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        if BaseUser.objects.filter(email=data['email']).exists():
            user = BaseUser.objects.get(email=data['email'])
            PasswordReset.objects.filter(user=user).update(voided_at=timezone.now())

            token = str(PasswordReset.objects.create(user=user).token)

            base_url = 'https://academy.hacksoft.io'
            reset_uri = 'forgot-password-set'
            reset_link = '/'.join([base_url, reset_uri, token])

            send_mail(
                recipients=[user.email],
                template_name='account_email_password_reset_key',
                context={
                    'password_reset_url': reset_link
                }
            )

        return Response(status=status.HTTP_202_ACCEPTED)


class ForgotPasswordSetApi(APIView):

    def post(self, request):
        serializer = PasswordResetSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        token.void()
        user = token.user
        user.set_password(serializer.validated_data['password'])
        user.save()

        return Response(status=status.HTTP_202_ACCEPTED)
