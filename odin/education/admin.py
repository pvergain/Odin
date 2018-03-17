from django.contrib import admin

from .models import (
    ProgrammingLanguage,
    Course,
    Task,
    Test,
    Solution
)


@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug_url')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'gradable')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'language')


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    pass
