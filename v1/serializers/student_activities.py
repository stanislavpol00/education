from rest_framework import serializers

from main.models import Student

from .episode import LightweightEpisodeSerializer
from .example import LightweightExampleSerializer
from .tip import LightweightTipSerializer


class StudentActivitiesSerializer(serializers.ModelSerializer):
    tips = LightweightTipSerializer(many=True)
    examples = LightweightExampleSerializer(many=True)
    episode_set = LightweightEpisodeSerializer(many=True)

    class Meta:
        model = Student
        fields = [
            "tips",
            "examples",
            "episode_set",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["episodes"] = representation.pop("episode_set")

        return representation
