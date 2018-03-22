from rest_framework import status
from rest_framework import serializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.settings import api_settings

from django.utils import timezone

from odin.emails.services import send_mail

from odin.users.models import BaseUser, Profile, PasswordResetToken
from odin.apis.mixins import ServiceExceptionHandlerMixin

from odin.education.apis.permissions import StudentCourseAuthenticationMixin

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class _ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.FileField(source='full_image')

    class Meta:
        model = Profile
        fields = ('full_name', 'avatar')


class _UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ('id', 'email')


class LoginUnitedApi(ObtainJSONWebToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = data.get('user')
        token = data.get('token')
        user_data = _UserSerializer(instance=user).data
        profile_data = _ProfileSerializer(instance=user.profile).data
        full_data = {**user_data, **profile_data}

        response_data = jwt_response_payload_handler(token, user, request)
        response_data.update({'me': full_data})

        return Response(response_data)


class UserDetailApi(StudentCourseAuthenticationMixin, APIView):
    def get(self, request):
        user = self.request.user
        user_data = _UserSerializer(instance=user).data
        profile_data = _ProfileSerializer(instance=user.profile).data
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
            PasswordResetToken.objects.filter(user=user).update(voided_at=timezone.now())

            token = str(PasswordResetToken.objects.create(user=user).token)

            reset_link = f'https://academy.hacksoft.io/forgot-password/{token}/'

            send_mail(
                recipients=[user.email],
                template_name='account_email_password_reset_key',
                context={
                    'password_reset_url': reset_link
                }
            )

        return Response(status=status.HTTP_202_ACCEPTED)


class ForgotPasswordSetApi(APIView):
    class Serializer(serializers.Serializer):
        password = serializers.CharField(required=True)
        token = serializers.PrimaryKeyRelatedField(
            queryset=PasswordResetToken.objects.all().filter(voided_at__isnull=True)
        )

    def post(self, request):
        serializer = self.Serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        token.void()
        token.use()
        user = token.user
        user.set_password(serializer.validated_data['password'])
        user.rotate_secret_key()
        user.save()

        return Response(status=status.HTTP_202_ACCEPTED)
