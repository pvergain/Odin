class ApplicationInfoFormDataMixin:
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            post_data = self.request.POST
            data = {}
            data['start_date'] = post_data.get('start_date')
            data['end_date'] = post_data.get('end_date')
            data['start_interview_date'] = post_data.get('start_interview_date')
            data['end_interview_date'] = post_data.get('end_interview_date')
            data['description'] = post_data.get('description')
            data['external_application_form'] = post_data.get('external_application_form')
            data['course'] = self.course.id

            form_kwargs['data'] = data
        return form_kwargs
