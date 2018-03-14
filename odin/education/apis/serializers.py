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
            fields = ('full_name',
                      'full_image',
                      'avatar',
                      )


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = BaseUser
        fields = ('id', 'email', 'profile')

        depth = 1
