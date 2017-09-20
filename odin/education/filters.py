import django_filters

from .models import Solution, Student


class SolutionsFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(method='filter_solutions')

    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task')
        super().__init__(*args, **kwargs)
        self.task = task

    def filter_solutions(self, queryset, name, value):
        if value == 'correct':
            return queryset.filter(solutions__task=self.task, solutions__status=Solution.OK)

        return queryset

    class Meta:
        model = Student
        fields = []
