from rest_framework import serializers

from .models import GraderPlainProblem, GraderBinaryProblem


class GraderPlainProblemSerializer(serializers.ModelSerializer):
    solution = serializers.CharField(source='encode_solution_text')
    test = serializers.CharField(source='encode_test_text')
    test_type = serializers.CharField(source='get_readable_test_type')
    file_type = serializers.CharField(source='get_readable_file_type')

    class Meta:
        model = GraderPlainProblem
        fields = [
            'test_type',
            'language',
            'file_type',
            'solution',
            'test',
            'extra_options'
        ]


class GraderBinaryProblemSerializer(serializers.ModelSerializer):
    solution = serializers.CharField(source='read_binary_file')
    test = serializers.CharField(source='read_binary_test')
    test_type = serializers.CharField(source='get_readable_test_type')
    file_type = serializers.CharField(source='get_readable_file_type')

    class Meta:
        model = GraderBinaryProblem
        fields = [
            'test_type',
            'language',
            'file_type',
            'solution',
            'test',
            'extra_options'
        ]


class GraderPlainProblemWithRequirementsSerializer(serializers.ModelSerializer):
    solution = serializers.CharField(source='encode_solution_text')
    test = serializers.CharField(source='return_encoded_test')
    test_type = serializers.CharField(source='get_readable_test_type')
    file_type = serializers.CharField(source='get_readable_file_type')

    class Meta:
        model = GraderPlainProblem
        fields = [
            'test_type',
            'language',
            'file_type',
            'solution',
            'test',
            'extra_options'
        ]
