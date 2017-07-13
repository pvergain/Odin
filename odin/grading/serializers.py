from rest_framework import serializers

from .models import GraderPlainProblem, GraderBinaryProblem

from .validators import validate_github_url


class GraderPlainProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraderPlainProblem
        fields = '__all__'


class GraderBinaryProblemSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='read_binary_file')
    test = serializers.CharField(source='read_binary_test')

    class Meta:
        model = GraderBinaryProblem
        fields = '__all__'
