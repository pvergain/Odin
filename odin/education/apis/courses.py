from rest_framework import serializers
from rest_framework.generics import ListAPIView

from odin.authentication.apis.permissions import JSONWebTokenAuthenticationMixin

from odin.education.models import Course


class StudentCoursesApi(JSONWebTokenAuthenticationMixin, ListAPIView):
    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = Course
            fields = ('id',
                      'name',
                      'start_date',
                      'end_date',
                      'logo',
                      'slug_url')

    serializer_class = Serializer

    def get_queryset(self):
        return Course.objects.all()
