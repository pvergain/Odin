from django.http import Http404


class CheckInterviewDataMixin:
    def interview_data_validation(self):
        self.application_id = self.kwargs.get('application')

        if self.interview is None or \
           self.interview.application is None or \
           self.interview.application.user != self.request.user or \
           self.interview.application.id != int(self.application_id):
            raise Http404
