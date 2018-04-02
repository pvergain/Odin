from django.contrib import admin

from odin.users.models import (
    BaseUser,
    Profile,
    PasswordResetToken
)


@admin.register(BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_student', 'is_teacher', 'is_superuser')
    search_fields = ('email',)
    ordering = ('id',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'user')


@admin.register(PasswordResetToken)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'voided_at', 'used_at', 'created_at', 'updated_at')
