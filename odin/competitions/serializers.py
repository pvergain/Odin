from rest_framework import serializers

from .models import Solution


class CompetitionSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ('id', 'url', 'task', 'code', 'check_status_location', 'build_id',
                  'status', 'test_output', 'return_code', 'file', 'participant')
