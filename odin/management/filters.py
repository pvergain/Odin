import django_filters

from odin.users.models import BaseUser


class UserFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(method="get_students_or_teachers")
    search = django_filters.CharFilter(method='filter_by_email')

    def get_students_or_teachers(self, queryset, name, value):
        if value == 'students':
            return queryset.filter(student__isnull=False)
        elif value == 'teachers':
            return queryset.filter(teacher__isnull=False)
        return queryset

    def filter_by_email(self, queryset, name, value):
        email_qs = set(queryset.filter(email__icontains=value))
        full_name_qs = set(queryset.filter(profile__full_name__icontains=value))
        queryset = list(email_qs.union(full_name_qs))
        return queryset

    class Meta:
        model = BaseUser
        fields = ['type']
