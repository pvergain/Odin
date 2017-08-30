from rest_framework import serializers

from odin.education.models import Topic, IncludedTask, Solution, IncludedMaterial


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ('url', 'code', 'check_status_location', 'build_id',
                  'status', 'test_output', 'return_code', 'file')


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncludedMaterial
        fields = ('identifier', 'url', 'content')


class TaskSerializer(serializers.ModelSerializer):
    solutions = SolutionSerializer(many=True)

    class Meta:
        model = IncludedTask
        fields = ('name', 'description', 'gradable', 'solutions')


class TopicSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)
    materials = MaterialSerializer(many=True)

    class Meta:
        model = Topic
        fields = ('name', 'tasks', 'materials')
