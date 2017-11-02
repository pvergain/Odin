import django_filters

from django.db.models import Q

from .models import Solution, Student


class SolutionsFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(method='filter_solutions')

    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task')
        super().__init__(*args, **kwargs)
        self.task = task

    def filter_solutions(self, queryset, name, value):
        if value == 'correct':
            q_expression = Q(solutions__task__gradable=True, solutions__status=Solution.OK) \
                         | Q(solutions__task__gradable=False, solutions__status=Solution.SUBMITTED_WITHOUT_GRADING)

            return queryset.filter(q_expression, solutions__task=self.task)

        return queryset

    class Meta:
        model = Student
        fields = []
