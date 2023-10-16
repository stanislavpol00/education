from main.models import StudentExample

from .base_updated_by import BaseUpdatedBySerializer
from .user import LightUserSerializer


class StudentExampleSerializer(BaseUpdatedBySerializer):
    added_by = LightUserSerializer(required=False)

    class Meta:
        model = StudentExample
        fields = [
            "id",
            "reason",
            "example",
            "student",
            "episode",
            "is_active",
            "added_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["added_by", "created_at", "updated_at"]
