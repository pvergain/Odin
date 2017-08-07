from django.contrib import admin

from .models import ProgrammingLanguage


@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
