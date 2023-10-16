from main.models import ExampleRating

from .base_updated_by import BaseUpdatedBySerializer
from .user import LightUserSerializer


class ExampleRatingSerializer(BaseUpdatedBySerializer):
    added_by = LightUserSerializer(required=False)

    class Meta:
        model = ExampleRating
        fields = [
            "id",
            "example",
            "added_by",
            "clarity",
            "recommended",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "added_by",
            "example",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        example_id = int(self.context["view"].kwargs["example_pk"])

        validated_data["example_id"] = example_id

        return super().create(validated_data)
