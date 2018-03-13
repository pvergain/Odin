from rest_framework.permissions import BasePermission

from odin.education.models import Student


class IsStudentPermission(BasePermission):
    """
    TODO: Write tests for that

    1) Initialize IsStudentPermission
    2) Call `has_permission` with `make_mock_object` for request, view
    3) Assert correctness
    """
    def has_permission(self, request, view):
        user = request.user
        student = user.downcast(Student)

        if student is not None:
            view.student = student
            return True

        return False
