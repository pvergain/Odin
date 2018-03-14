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
        avatar = serializers.FileField(source='full_image')

        class Meta:
            model = Profile
            fields = ('full_name',
                      'avatar',
                      )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUser
        fields = ('id', 'email')
