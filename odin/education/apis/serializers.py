from rest_framework import serializers

from odin.users.models import BaseUser, Profile

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
