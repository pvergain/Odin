from typing import Dict


def get_email_template_context(*,
                               context: Dict[str, str] = {}
                               ) -> Dict[str, str]:
    template_context = {}

    user = context.get('user')
    current_site = context.get('current_site')
    if user:
        template_context['user'] = user.email
    if current_site:
        template_context['current_site'] = current_site.name
    template_context['activate_url'] = context.get('activate_url')
    template_context['password_reset_url'] = context.get('password_reset_url')
    template_context['key'] = context.get('key')

    return template_context
