from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter

from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from odin.common.services import send_email
from .helpers import get_email_template_context


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

        template_context = get_email_template_context(context=context)

        send_email(
            template_name=settings.EMAIL_TEMPLATES[template_prefix],
            recipients=[email],
            context=template_context
        )

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        competition_data = request.session.get('competition_data')
        if competition_data:
            current_site = get_current_site(request)
            activate_url = self.get_email_confirmation_url(
                request,
                emailconfirmation
            ) + f'?competition_slug={competition_data.get("competition_slug")}'
            ctx = {
                "user": emailconfirmation.email_address.user,
                "activate_url": activate_url,
                "current_site": current_site,
                "key": emailconfirmation.key,

            }
            email_template = 'account/email/email_competition_confirmation'
            self.send_mail(email_template,
                           emailconfirmation.email_address.email,
                           ctx)
        else:
            super().send_confirmation_mail(request, emailconfirmation, signup)

    def add_message(self, request, level, message_template,
                    message_context=None, extra_tags=''):
        """
        Required to disable django-allauth's default messaging feedback
        upon email confirmation, user creation, and login
        """
        pass
