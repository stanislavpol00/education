from taggit.serializers import TaggitSerializer, TagListSerializerField

from main.models import Example

from .base_updated_by import BaseUpdatedBySerializer
from .user import LightUserSerializer


class LightweightExampleSerializer(BaseUpdatedBySerializer):
    updated_by = LightUserSerializer(required=False)
    added_by = LightUserSerializer(required=False)

    class Meta:
        model = Example
        fields = [
            "id",
            "tip",
            "description",
            "example_type",
            "context_notes",
            "sounds_like",
            "looks_like",
            "episode",
            "is_active",
            "goal",
            "is_workflow_completed",
            "is_bookmarked",
            "headline",
            "heading",
            "situation",
            "shadows_response",
            "outcome",
            "updated_by",
            "added_by",
            "added",
            "updated",
            "updated_at",
            "created_at",
            "episode_student_id",
        ]
        read_only_fields = [
            "updated_by",
            "added_by",
            "added",
            "updated",
            "updated_at",
            "created_at",
        ]


class ExampleSerializer(TaggitSerializer, LightweightExampleSerializer):
    tags = TagListSerializerField(required=False)

    class Meta(LightweightExampleSerializer.Meta):
        fields = LightweightExampleSerializer.Meta.fields + [
            "average_rating",
            "clarity_average_rating",
            "recommended_average_rating",
            "tags",
            "student_ids",
        ]
