from rest_framework import serializers

from django.urls import reverse

from .models import Interview


class InterviewSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format='%d:%m:%Y')
    start_time = serializers.TimeField(format='%H:%M')
    choose_interview_url = serializers.SerializerMethodField()

    def get_choose_interview_url(self, obj):
        return reverse('dashboard:interviews:choose-interview',
                       kwargs={'application_id': self.context['application'],
                               'interview_token': obj.uuid})

    class Meta:
        model = Interview
        fields = ('date', 'start_time', 'choose_interview_url')
