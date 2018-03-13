'''
stuent_id >> CourseAssignment >> course >> topic >> All included task >>Solution

new solution << student + IncludedTask
'''
from rest_framework import serializers

from odin.education.models import IncludedTask


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncludedTask
        fields = ('name', 'description', 'gradable')
