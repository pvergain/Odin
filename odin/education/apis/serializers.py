from rest_framework import serializers

from odin.education.models import IncludedTask


class SolutionSubmitSerializer(serializers.Serializer):
    task = serializers.PrimaryKeyRelatedField(queryset=IncludedTask.objects.all())
    code = serializers.CharField(required=False)
    url = serializers.URLField(required=False)
