from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

from odin.common.services import send_email


class CustomAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        """
        Required to bypass the automatic user population
        """
        pass

    def get_signup_form_initial_data(self, sociallogin):
        """
        Required to bypass automatic initial form data override
        """
        pass


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        template_prefix = template_prefix.replace('/', '_')

        if context.get('request'):
            context.pop('request')
        context['current_site'] = context['current_site'].name
        context['user'] = context['user'].email

        send_email(
            template_name=settings.EMAIL_TEMPLATES[template_prefix],
            recipients=[email],
            context=context
        )
