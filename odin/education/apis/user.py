from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response

from odin.education.models import BaseUser

from .permissions import StudentCourseAuthenticationMixin


class UserDetailApi(StudentCourseAuthenticationMixin, APIView):
    class UserSerializer(serializers.ModelSerializer):
        profile = serializers.SerializerMethodField()

        class Meta:
            model = BaseUser
            fields = ('id',
                      'name',
                      'email',
                      'profile'
                      )

        def get_profile(self, obj):
            import ipdb; ipdb.set_trace()
            return {
                    'full_image': obj.profile.full_image.path,
                    'full_name': obj.profile.full_name,
                    'skype': obj.profile.skype,
                    'social_accounts': obj.socials,
                    'studies_at': obj.profile.studies_at,
                    'works_at': obj.profile.works_at
                }

    def get(self, request):
        user = self.request.user
        if user.profile.social_accounts:
            user.socials = {key:value for key,value in user.profile.social_accounts.items()}
        else:
            user.socials = None

        return Response(self.UserSerializer(instance=user).data)
