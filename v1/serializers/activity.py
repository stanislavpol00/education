from main.models import Activity

from .base_updated_by import BaseUpdatedBySerializer
from .user import LightUserSerializer


class ActivitySerializer(BaseUpdatedBySerializer):
    user = LightUserSerializer(required=False)

    class Meta:
        model = Activity
        fields = [
            "id",
            "type",
            "user",
            "meta",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "created_at",
        ]
