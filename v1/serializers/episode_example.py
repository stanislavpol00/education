from main.models import Example

from .base_updated_by import BaseUpdatedBySerializer
from .user import LightUserSerializer


class EpisodeExampleSerializer(BaseUpdatedBySerializer):
    updated_by = LightUserSerializer(required=False)

    class Meta:
        model = Example
        fields = [
            "id",
            "tip",
            "episode",
            "description",
            "example_type",
            "context_notes",
            "sounds_like",
            "looks_like",
            "updated_by",
            "updated",
            "is_active",
            "goal",
            "is_workflow_completed",
            "headline",
            "heading",
            "situation",
            "shadows_response",
            "outcome",
        ]
        read_only_fields = [
            "updated_by",
            "updated",
            "episode",
            "added_by",
        ]

    def create(self, validated_data):
        episode_id = int(self.context["view"].kwargs["episode_pk"])

        validated_data["episode_id"] = episode_id

        return super().create(validated_data)
