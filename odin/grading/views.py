from rest_framework.views import APIView

from django.conf import settings

from .services import create_plain_problem, create_binary_problem


class SolutionsAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        code = data.get('code')
        file = data.get('file')
        solution_id = data.get('solution_id')
        solution_model = settings.GRADER_SOLUTION_MODEL

        solution = get_object_or_404(solution_model, id=solution_id)

        if code and not file:
            plain_problem = create_plain_problem()
