from rest_framework import status
from rest_framework import serializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.settings import api_settings
from odin.authentication.permissions import JSONWebTokenAuthenticationMixin

from django.db.models.query import Q

from odin.users.models import BaseUser, PasswordResetToken
from odin.apis.mixins import ServiceExceptionHandlerMixin

from odin.authentication.services import (
    logout,
    get_user_data,
    initiate_reset_user_password,
    reset_user_password,
    change_user_password,
)

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class LoginApi(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = data.get('user')
        token = data.get('token')

        full_data = get_user_data(user=user)

        response_data = jwt_response_payload_handler(token, user, request)
        response_data.update({'me': full_data})

        return Response(response_data)


class UserDetailApi(JSONWebTokenAuthenticationMixin, APIView):
    def get(self, request):
        full_data = get_user_data(user=self.request.user)

        return Response(full_data)


class LogoutApi(JSONWebTokenAuthenticationMixin, APIView):
    def post(self, request):
        logout(user=self.request.user)

        return Response(status=status.HTTP_202_ACCEPTED)


class ForgotPasswordApi(ServiceExceptionHandlerMixin, APIView):
    class Serializer(serializers.Serializer):
        user = serializers.SlugRelatedField(
            queryset=BaseUser.objects.all(),
            slug_field='email',
            error_messages={
                'does_not_exist':
                ('User with that email does not exist')
            }
        )

    def post(self, request):
        serializer = self.Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        initiate_reset_user_password(user=data['user'])

        return Response(status=status.HTTP_202_ACCEPTED)


class ForgotPasswordSetApi(ServiceExceptionHandlerMixin, APIView):
    class Serializer(serializers.Serializer):
        password = serializers.CharField()

        token = serializers.PrimaryKeyRelatedField(
            queryset=PasswordResetToken.objects.filter(
                Q(voided_at__isnull=True) | Q(used_at__isnull=True)
            )
        )

    def post(self, request):
        serializer = self.Serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        reset_user_password(
            token=data['token'],
            password=data['password']
        )

        return Response(status=status.HTTP_202_ACCEPTED)


class ChangePasswordApi(
    ServiceExceptionHandlerMixin,
    JSONWebTokenAuthenticationMixin,
    APIView
):

    def post(self, request):
        data = {**request.data}
        data['user'] = self.request.user

        change_user_password(**data)

        return Response(status=status.HTTP_202_ACCEPTED)
