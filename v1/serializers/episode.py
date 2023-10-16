from taggit.serializers import TaggitSerializer, TagListSerializerField

from main.models import Episode

from .base_updated_by import BaseUpdatedBySerializer
from .user import LightUserSerializer


class EpisodeSerializer(TaggitSerializer, BaseUpdatedBySerializer):
    user = LightUserSerializer(required=False)
    contributors = LightUserSerializer(required=False, many=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Episode
        fields = [
            "id",
            "student",
            "user",
            "title",
            "description",
            "description_html",
            "description_ids",
            "heads_up",
            "transcript_html",
            "transcript",
            "transcript_ids",
            "is_active",
            "date",
            "full",
            "landmark",
            "heads_up_json",
            "contributors",
            "tags",
            "practitioner",
            "created_at",
        ]
        read_only_fields = ["user"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.practitioner_id:
            representation["practitioner"] = LightUserSerializer(
                instance.practitioner
            ).data

        return representation


class LightweightEpisodeSerializer(BaseUpdatedBySerializer):
    user = LightUserSerializer(required=False)

    class Meta:
        model = Episode
        fields = [
            "id",
            "student",
            "user",
            "title",
            "description",
            "description_html",
            "description_ids",
            "heads_up",
            "transcript_html",
            "transcript",
            "transcript_ids",
            "is_active",
            "date",
            "full",
            "landmark",
            "heads_up_json",
            "created_at",
        ]
        read_only_fields = ["user"]
