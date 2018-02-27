from django.contrib import admin

from odin.users.models import BaseUser


@admin.register(BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_student', 'is_teacher', 'is_participant', 'is_superuser')
    search_fields = ('email',)
    ordering = ('id',)
