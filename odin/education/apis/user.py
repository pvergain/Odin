from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response

from odin.users.models import Profile

from .permissions import StudentCourseAuthenticationMixin


class UserDetailApi(StudentCourseAuthenticationMixin, APIView):
    class UserSerializer(serializers.ModelSerializer):
        user = serializers.SerializerMethodField()

        class Meta:
            model = Profile
            fields = ('id',
                      'full_name',
                      'full_image',
                      'skype',
                      'studies_at',
                      'social_accounts',
                      'works_at',
                      'user'
                      )

        def get_user(self, obj):
            return {
                    'name': obj.user.name,
                    'email': obj.user.email,
                }

    def get(self, request):
        profile = Profile.objects.get(id=self.request.user.id)
        profile.name = self.request.user.name
        profile.email = self.request.user.email

        return Response(self.UserSerializer(instance=profile).data)
