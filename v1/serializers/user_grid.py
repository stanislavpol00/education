from rest_framework import serializers

from main.models import Example, Tip, User

from .recent_activity import (
    RecentActivityExampleSerializer,
    RecentActivityTipSerializer,
)
from .student import StudentSerializer


class UserGridSerializer(serializers.ModelSerializer):
    assigned_students = serializers.SerializerMethodField()
    tips = serializers.SerializerMethodField()
    examples = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "last_activity",
            "assigned_students",
            "tips",
            "examples",
        ]
        read_only_fields = fields

    def get_tips(self, obj):
        activities = self.context["last_activities"]

        if obj.id not in activities:
            return []

        content_types = self.context["content_types"]
        all_action_objects = self.context["all_action_objects"]
        tip_activities = activities[obj.id].get(content_types[Tip].id)
        tips = self.add_contributed_at(tip_activities, all_action_objects[Tip])

        return RecentActivityTipSerializer(tips, many=True).data

    def get_examples(self, obj):
        activities = self.context["last_activities"]

        if obj.id not in activities:
            return []

        content_types = self.context["content_types"]
        all_action_objects = self.context["all_action_objects"]
        example_activities = activities[obj.id].get(content_types[Example].id)
        examples = self.add_contributed_at(
            example_activities, all_action_objects[Example]
        )

        return RecentActivityExampleSerializer(examples, many=True).data

    def get_assigned_students(self, obj):
        user_students = self.context["user_students"]

        if obj.id not in user_students:
            return []

        students = user_students[obj.id]

        return StudentSerializer(students, many=True).data

    def get_last_activity(self, obj):
        user_last_activity = self.context["user_last_activity"]
        if obj.id not in user_last_activity:
            return None

        return user_last_activity[obj.id]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["practitioner"] = {
            "id": representation.pop("id"),
            "first_name": representation.pop("first_name"),
            "last_name": representation.pop("last_name"),
            "full_name": representation.pop("full_name"),
            "last_activity": representation.pop("last_activity"),
            "assigned_students": representation.pop("assigned_students"),
        }

        return representation

    def add_contributed_at(self, action_objects, objects):
        if not action_objects:
            return []

        result = []
        for action_object in action_objects:
            for object_id, timestamp in action_object.items():
                obj = objects[object_id]
                obj.contributed_at = timestamp
                result.append(obj)

        return sorted(
            result, key=lambda item: item.contributed_at, reverse=True
        )
