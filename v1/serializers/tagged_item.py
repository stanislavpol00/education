from rest_framework import serializers
from taggit.models import TaggedItem

from .tag import TagSerializer


class LightweightTaggedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaggedItem
        fields = [
            "id",
            "object_id",
            "content_type",
            "tag",
        ]


class TaggedItemSerializer(serializers.ModelSerializer):
    tag = TagSerializer(required=False)

    class Meta:
        model = TaggedItem
        fields = [
            "id",
            "object_id",
            "content_type",
            "tag",
        ]
        read_only_fields = fields
