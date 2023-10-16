from notifications.models import Notification
from rest_framework import serializers

import constants

from .user import LightUserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "verb",
            "unread",
            "timestamp",
            "description",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.verb in constants.Activity.REPRESENTED_VERBS:
            function_name = "get_action_object_for_{}".format(instance.verb)
            representation["action_object"] = getattr(self, function_name)(
                instance
            )

        representation["actor"] = LightUserSerializer(instance.actor).data
        representation["created_at"] = representation.pop("timestamp")

        return representation

    def get_action_object_for_create_episode(self, instance):
        data = {
            "episode": None,
            "student": None,
            "student_nickname": None,
        }

        episode = instance.action_object
        if episode:
            data = {
                "episode": episode.id,
                "student": episode.student_id,
                "student_nickname": episode.student.nickname,
            }

        return data

    def get_action_object_for_suggest_tip(self, instance):
        data = {
            "tip": None,
            "student": None,
            "student_nickname": None,
        }

        student_tip = instance.action_object
        if student_tip:
            data = {
                "tip": student_tip.tip_id,
                "student": student_tip.student_id,
                "student_nickname": student_tip.student.nickname,
            }

        return data

    def get_action_object_for_assign_student(self, instance):
        data = {
            "student": None,
            "student_nickname": None,
        }

        user_student_mapping = instance.action_object
        if user_student_mapping:
            data = {
                "student": user_student_mapping.student_id,
                "student_nickname": user_student_mapping.student.nickname,
            }

        return data

    def get_action_object_for_attach_tip_with_example(self, instance):
        example = instance.action_object
        data = {
            "tip": example.tip_id,
            "example": example.id,
        }

        return data

    def get_action_object_for_set_tip_edit_mark(self, instance):
        data = {
            "tip": None,
        }

        tip = instance.action_object
        if tip:
            data = {
                "tip": tip.id,
            }

        return data

    def get_action_object_for_attach_related_tips_with_tip(self, instance):
        data = {
            "tip": None,
        }

        tip = instance.action_object
        if tip:
            data = {
                "tip": tip.id,
            }

        return data


class LightweightNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "verb",
            "timestamp",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["created_at"] = representation.pop("timestamp")

        return representation
