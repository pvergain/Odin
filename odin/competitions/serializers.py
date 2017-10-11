from rest_framework import serializers

from .models import (
    Solution,
    CompetitionMaterial,
    CompetitionTask,
    CompetitionTest,
    Competition
)


class CompetitionSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ('id', 'url', 'task', 'code', 'check_status_location', 'build_id',
                  'status', 'test_output', 'return_code', 'file', 'participant')


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionMaterial
        fields = ('id', 'identifier', 'url')


class TestSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField()
    source = serializers.BooleanField(source='is_source')

    class Meta:
        model = CompetitionTest
        fields = ('language', 'source')


class TaskSerializer(serializers.ModelSerializer):
    solutions = CompetitionSolutionSerializer(many=True)
    test = TestSerializer()

    class Meta:
        model = CompetitionTask
        fields = ('id', 'name', 'test', 'description', 'gradable', 'solutions')


class CompetitionSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)
    materials = MaterialSerializer(many=True)

    class Meta:
        model = Competition
        fields = ('id', 'name', 'tasks', 'materials', 'slug_url')
