import django_filters

from main.models import Task


class TaskFilter(django_filters.FilterSet):
    class Meta:
        model = Task
        fields = [
            "user",
            "tip",
            "student",
            "added_by",
            "task_type",
        ]
