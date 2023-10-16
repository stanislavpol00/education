from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

import constants
from main.models import Tip

from .base_updated_by import BaseUpdatedBySerializer
from .user import LightUserSerializer


class TipSerializer(TaggitSerializer, BaseUpdatedBySerializer):
    updated_by = LightUserSerializer(required=False)
    created_by = LightUserSerializer(required=False)
    added_by = LightUserSerializer(required=False)
    read_count = serializers.IntegerField(default=0, read_only=True)
    try_count = serializers.IntegerField(default=0, read_only=True)
    is_rated = serializers.BooleanField(default=False, read_only=True)
    helpful_count_by_user = serializers.IntegerField(default=0, read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Tip
        fields = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "description",
            "group_context",
            "helpful",
            "howto",
            "when",
            "persuasive",
            "sub_goal",
            "related_tips",
            "overarching_goal",
            "updated_by",
            "child_context",
            "child_context_flattened",
            "environment_context",
            "environment_context_flattened",
            "linked_tips",
            "marked_for_editing",
            "average_rating",
            "clarity_average_rating",
            "relevance_average_rating",
            "uniqueness_average_rating",
            "created_at",
            "created_by",
            "updated_at",
            "updated",
            "added_by",
            "read_count",
            "try_count",
            "is_rated",
            "helpful_count_by_user",
            "tags",
            "tip_summary",
        ]
        read_only_fields = [
            "updated_by",
            "created_at",
            "updated_at",
            "updated",
            "added_by",
            "read_count",
            "try_count",
            "is_rated",
            "helpful_count_by_user",
        ]

    def validate_child_context(self, value):
        keys = set(value.keys())
        allowed_keys = set(constants.ChildContext.VALUES)

        is_valid = keys.issubset(allowed_keys)
        if not is_valid:
            raise serializers.ValidationError(_("Invalid child context"))

        return value

    def validate_environment_context(self, value):
        keys = set(value.keys())
        allowed_keys = set(constants.Environment.VALUES)

        is_valid = keys.issubset(allowed_keys)
        if not is_valid:
            raise serializers.ValidationError(_("Invalid environment context"))

        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["helpful_count"] = representation.pop(
            "helpful_count_by_user"
        )
        return representation


class StatsTipSerializer(serializers.ModelSerializer):
    read_count = serializers.IntegerField(default=0)
    try_count = serializers.IntegerField(default=0)
    is_rated = serializers.BooleanField(default=False)
    helpful_count_by_user = serializers.IntegerField(default=0)

    class Meta:
        model = Tip
        fields = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "marked_for_editing",
            "read_count",
            "try_count",
            "is_rated",
            "helpful_count_by_user",
            "tip_summary",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["helpful_count"] = representation.pop(
            "helpful_count_by_user"
        )
        return representation


class LightweightTipSerializer(serializers.ModelSerializer):
    read_count = serializers.IntegerField(default=0)

    class Meta:
        model = Tip
        fields = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "marked_for_editing",
            "read_count",
            "tip_summary",
        ]
        read_only_fields = fields


class LightweightRecentTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tip
        fields = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "marked_for_editing",
            "added_by",
            "updated_by",
            "created_at",
            "tip_summary",
        ]
        read_only_fields = fields


class DLPTipSerializer(TaggitSerializer, serializers.ModelSerializer):
    created_by = LightUserSerializer(required=False)
    added_by = LightUserSerializer(required=False)
    updated_by = LightUserSerializer(required=False)
    is_rated = serializers.BooleanField(default=False)
    read_count = serializers.IntegerField(default=0)
    try_count = serializers.IntegerField(default=0)
    helpful_count_by_user = serializers.IntegerField(default=0)
    graduated_for = serializers.ListField(default=[])
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Tip
        fields = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "description",
            "group_context",
            "helpful",
            "helpful_count_by_user",
            "howto",
            "when",
            "persuasive",
            "sub_goal",
            "related_tips",
            "overarching_goal",
            "updated_by",
            "child_context",
            "child_context_flattened",
            "environment_context",
            "environment_context_flattened",
            "linked_tips",
            "marked_for_editing",
            "average_rating",
            "clarity_average_rating",
            "relevance_average_rating",
            "uniqueness_average_rating",
            "created_at",
            "updated_at",
            "updated",
            "added_by",
            "is_rated",
            "read_count",
            "try_count",
            "graduated_for",
            "tags",
            "created_by",
            "tip_summary",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["helpful_count"] = representation.pop(
            "helpful_count_by_user"
        )
        return representation


class LightweightDLPTipSerializer(serializers.ModelSerializer):
    read_count = serializers.IntegerField(default=0)
    try_count = serializers.IntegerField(default=0)
    is_rated = serializers.BooleanField(default=False)
    helpful_count_by_user = serializers.IntegerField(default=0)
    graduated_for = serializers.ListField(default=[])

    class Meta:
        model = Tip
        fields = [
            "id",
            "state",
            "substate",
            "levels",
            "title",
            "marked_for_editing",
            "helpful_count_by_user",
            "read_count",
            "try_count",
            "is_rated",
            "graduated_for",
            "tip_summary",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["helpful_count"] = representation.pop(
            "helpful_count_by_user"
        )
        return representation
