from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from main.models import Student


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "nickname",
            "is_active",
            "image",
            "visible_for_guest",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]


class LightweightStudentSerializer(serializers.ModelSerializer):
    number_of_tips = serializers.SerializerMethodField()
    number_of_episodes = serializers.SerializerMethodField()
    last_activity_timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "nickname",
            "is_active",
            "image",
            "visible_for_guest",
            "created_at",
            "updated_at",
            "number_of_tips",
            "number_of_episodes",
            "last_activity_timestamp",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "number_of_tips",
            "number_of_episodes",
            "last_activity_timestamp",
        ]

    def get_number_of_tips(self, obj):
        if obj.id not in self.context["student_tips"]:
            return 0
        return self.context["student_tips"][obj.id]

    def get_number_of_episodes(self, obj):
        if obj.id not in self.context["student_episodes"]:
            return 0
        return self.context["student_episodes"][obj.id]

    def get_last_activity_timestamp(self, obj):
        if obj.id not in self.context["last_activity_timestamps_on_students"]:
            return None
        return self.context["last_activity_timestamps_on_students"][obj.id]


class StudentDetailSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "nickname",
            "is_active",
            "image",
            "visible_for_guest",
            "last_month_heads_up",
            "monitoring",
            "created_at",
            "updated_at",
            "tags",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]
