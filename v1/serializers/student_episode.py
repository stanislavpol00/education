from main.models import Episode

from .base_updated_by import BaseUpdatedBySerializer
from .user import LightUserSerializer


class StudentEpisodeSerializer(BaseUpdatedBySerializer):
    user = LightUserSerializer(required=False)
    writers = LightUserSerializer(required=False, many=True)

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
            "writers",
            "practitioner",
        ]
        read_only_fields = ["student", "user"]

    def create(self, validated_data):
        student_id = int(self.context["view"].kwargs["student_pk"])

        validated_data["student_id"] = student_id

        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.practitioner_id:
            representation["practitioner"] = LightUserSerializer(
                instance.practitioner
            ).data

        return representation
