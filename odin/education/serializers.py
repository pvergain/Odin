from rest_framework import serializers

from odin.education.models import Topic, IncludedTask, Solution, IncludedMaterial


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ('id', 'url', 'code', 'check_status_location', 'build_id',
                  'status', 'test_output', 'return_code', 'file', 'student')


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncludedMaterial
        fields = ('id', 'identifier', 'url', 'content')


class TaskSerializer(serializers.ModelSerializer):
    solutions = SolutionSerializer(many=True)

    class Meta:
        model = IncludedTask
        fields = ('id', 'name', 'description', 'gradable', 'solutions')


class TopicSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)
    materials = MaterialSerializer(many=True)

    class Meta:
        model = Topic
        fields = ('id', 'name', 'tasks', 'materials')
