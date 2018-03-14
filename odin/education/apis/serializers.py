'''
stuent_id >> CourseAssignment >> course >> topic >> All included task >>Solution

new solution << student + IncludedTask
'''
from rest_framework import serializers

from odin.education.models import IncludedTask

from odin.users.models import BaseUser, Profile


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncludedTask
        fields = ('name', 'description', 'gradable')


class ProfileSerializer(serializers.ModelSerializer):
        class Meta:
            model = Profile
            fields = ('id',
                      'full_name',
                      'full_image',
                      'skype',
                      'avatar',
                      'studies_at',
                      'social_accounts',
                      'works_at')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = BaseUser
        fields = ('id', 'name', 'email', 'profile')
