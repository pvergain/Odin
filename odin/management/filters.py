import django_filters
from django.db.models import Q

from odin.users.models import BaseUser


class UserFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(method="get_students_or_teachers")
    search_field = django_filters.CharFilter(method='search')

    def get_students_or_teachers(self, queryset, name, value):
        if value == 'students':
            return queryset.filter(student__isnull=False)
        elif value == 'teachers':
            return queryset.filter(teacher__isnull=False)
        return queryset

    def search(self, queryset, name, value):
        queryset = queryset.filter(Q(email__icontains=value) | Q(profile__full_name__icontains=value))
        return queryset

    class Meta:
        model = BaseUser
        fields = ['type']
