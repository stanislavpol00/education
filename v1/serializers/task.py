from main.models import Task

from .base_updated_by import BaseUpdatedBySerializer
from .user import LightUserSerializer


class TaskSerializer(BaseUpdatedBySerializer):
    added_by = LightUserSerializer(required=False)

    class Meta:
        model = Task
        fields = [
            "id",
            "user",
            "tip",
            "student",
            "added_by",
            "task_type",
            "info",
            "reporter_note",
            "assignee_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "added_by",
            "created_at",
            "updated_at",
        ]
