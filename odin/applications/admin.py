from django.contrib import admin

from odin.applications.models import Application, ApplicationInfo


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    pass


@admin.register(ApplicationInfo)
class ApplicationInfoAdmin(admin.ModelAdmin):
    pass
