from django.contrib import admin

from .models import (
    ProgrammingLanguage,
    Course,
    Task,
    IncludedTask,
    Topic,
    Week,
    Test,
    Solution,
    CourseAssignment,
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


@admin.register(IncludedTask)
class IncludedTaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'topic')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'week')


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ('number', 'course', 'start_date', 'end_date')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'language')


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    pass


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'course', 'hidden')
