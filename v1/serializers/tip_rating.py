from django.utils import timezone
from rest_framework import serializers

from main.models import Student, TipRating
from tasks import notification

from .base_updated_by import BaseUpdatedBySerializer
from .user import LightUserSerializer


class TipRatingSerializer(BaseUpdatedBySerializer):
    added_by = LightUserSerializer(required=False)

    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = TipRating
        fields = [
            "id",
            "tip",
            "added_by",
            "student",
            "clarity",
            "relevance",
            "uniqueness",
            "comment",
            "commented_at",
            "read_count",
            "try_count",
            "try_comment",
            "tried_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "added_by",
            "tip",
            "created_at",
            "updated_at",
            "read_count",
            "try_count",
            "try_comment",
            "tried_at",
            "commented_at",
        ]

    def validate(self, data):
        validated_data = super().validate(data)

        if "comment" in validated_data:
            validated_data["commented_at"] = timezone.localtime()

        return validated_data

    def create(self, validated_data):
        user = self.context["request"].user
        tip_id = int(self.context["view"].kwargs["tip_pk"])

        student = validated_data.pop("student", None)
        instance, _ = TipRating.objects.update_or_create(
            tip_id=tip_id,
            added_by=user,
            student=student,
            defaults=validated_data,
        )
        if "comment" in validated_data:
            notification.create_notifications.delay(
                instance.generate_comment_tip_rating_notification()
            )

        return instance
