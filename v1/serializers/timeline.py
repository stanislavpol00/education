from rest_framework import serializers

from main.models import Timeline


class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = ["id", "name", "is_default", "days"]
