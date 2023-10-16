from rest_framework import serializers

from main.models import Example, Tip

from .example import LightweightExampleSerializer
from .tip import LightweightTipSerializer


class RecentActivityTipSerializer(LightweightTipSerializer):
    contributed_at = serializers.DateTimeField(required=True)

    class Meta:
        model = Tip
        fields = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "marked_for_editing",
            "contributed_at",
        ]
        read_only_fields = fields


class RecentActivityExampleSerializer(LightweightExampleSerializer):
    contributed_at = serializers.DateTimeField(required=True)

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
            "contributed_at",
        ]
        read_only_fields = [
            "updated_by",
            "added_by",
            "added",
            "updated",
            "updated_at",
            "created_at",
            "contributed_at",
        ]
