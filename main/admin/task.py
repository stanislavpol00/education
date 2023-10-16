from django.contrib import admin

from ..models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tip", "student")
    list_display_links = ("user", "tip", "student")
