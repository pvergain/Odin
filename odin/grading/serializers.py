from rest_framework import serializers

from .models import GraderPlainProblem, GraderBinaryProblem


class GraderPlainProblemSerializer(serializers.ModelSerializer):
    solution = serializers.CharField(source='encode_solution_text')
    test = serializers.CharField(source='encode_test_text')

    class Meta:
        model = GraderPlainProblem
        fields = '__all__'


class GraderBinaryProblemSerializer(serializers.ModelSerializer):
    solution = serializers.CharField(source='read_binary_file')
    test = serializers.CharField(source='read_binary_test')

    class Meta:
        model = GraderBinaryProblem
        fields = '__all__'
