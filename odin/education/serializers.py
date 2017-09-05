from rest_framework import serializers

from odin.education.models import (
    Topic,
    IncludedTask,
    Solution,
    IncludedMaterial,
    IncludedTest
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

    class Meta:
        model = IncludedTest
        fields = ('language', )


class TaskSerializer(serializers.ModelSerializer):
    solutions = SolutionSerializer(many=True)
    test = TestSerializer()

    class Meta:
        model = IncludedTask
        fields = ('id', 'test', 'name', 'description', 'gradable', 'solutions')


class TopicSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)
    materials = MaterialSerializer(many=True)

    class Meta:
        model = Topic
        fields = ('id', 'name', 'tasks', 'materials', 'course')
