from django.contrib import admin

from odin.users.models import (
    BaseUser,
    Profile,
    PasswordReset
)


@admin.register(BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_student', 'is_teacher', 'is_participant', 'is_superuser')
    search_fields = ('email',)
    ordering = ('id',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'user')


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'reset_key')
