from .utils import get_readable_form_errors


class ReadableFormErrorsMixin:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        form = context.get('form')
        context['readable_errors'] = get_readable_form_errors(form)
        return context
