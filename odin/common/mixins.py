from typing import Dict, Callable

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError

from .utils import get_readable_form_errors


class BaseUserPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return True


class ReadableFormErrorsMixin:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        form = context.get('form')
        context['readable_errors'] = get_readable_form_errors(form)
        return context


class CallServiceMixin:
    def get_service(self):
        raise ImproperlyConfigured('CallServiceMixin requires service.')

    def call_service(self,
                     *,
                     service: Callable=None,
                     service_kwargs: Dict=None):
        if service is None:
            service = self.get_service()

        try:
            return service(**service_kwargs)
        except ValidationError as e:
            messages.warning(request=self.request, message=str(e))
