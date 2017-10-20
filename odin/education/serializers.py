from rest_framework import serializers

from odin.education.models import (
    Topic,
    IncludedTask,
    Solution,
    IncludedMaterial,
    IncludedTest,
    Week
)


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ('id', 'url', 'code', 'check_status_location', 'build_id',
                  'status', 'test_output', 'return_code', 'file', 'student')


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncludedMaterial
        fields = ('id', 'identifier', 'url', 'content')


class TestSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField()
    source = serializers.BooleanField(source='is_source')

    class Meta:
        model = IncludedTest
        fields = ('language', 'source')


class TaskSerializer(serializers.ModelSerializer):
    solutions = SolutionSerializer(many=True)
    test = TestSerializer()

    class Meta:
        model = IncludedTask
        fields = ('id', 'test', 'name', 'description', 'gradable', 'solutions')


class WeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Week
        fields = ('id', 'number')


class TopicSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)
    materials = MaterialSerializer(many=True)
    week = WeekSerializer()

    class Meta:
        model = Topic
        fields = ('id', 'name', 'tasks', 'materials', 'course', 'week')
