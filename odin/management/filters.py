import django_filters

from odin.users.models import BaseUser


class UserFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(method="get_students_or_teachers")

    def get_students_or_teachers(self, queryset, name, value):
        if value == 'students':
            return queryset.filter(student__isnull=False)
        elif value == 'teachers':
            return queryset.filter(teacher__isnull=False)
        return queryset

    class Meta:
        model = BaseUser
        fields = ['type']
