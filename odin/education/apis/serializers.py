from rest_framework import serializers

from odin.users.models import BaseUser, Profile, PasswordReset

from odin.education.models import IncludedTask


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.FileField(source='full_image')

    class Meta:
        model = Profile
        fields = ('full_name', 'avatar')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ('id', 'email')


class SolutionSubmitSerializer(serializers.Serializer):
    task = serializers.PrimaryKeyRelatedField(queryset=IncludedTask.objects.all())
    code = serializers.CharField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    token = serializers.PrimaryKeyRelatedField(
        queryset=PasswordReset.objects.all().filter(voided_at__isnull=True))
