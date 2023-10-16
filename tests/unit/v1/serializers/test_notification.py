from django.test import TestCase
from django.utils import timezone

from v1.serializers import (
    LightweightNotificationSerializer,
    NotificationSerializer,
)


class TestNotificationSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.notification = type(
            "Notification",
            (),
            {
                "id": 1,
                "level": "info",
                "verb": "Hello",
                "unread": True,
                "timestamp": timezone.localtime(),
                "actor_object_id": 1,
                "actor": type("User", (), {"id": 1, "full_name": "joe"}),
            },
        )

        cls.valid_key = [
            "id",
            "verb",
            "unread",
            "created_at",
            "actor",
        ]

    def test_to_representation(self):
        serializer = NotificationSerializer(self.notification)

        self.assertListEqual(
            sorted(self.valid_key), sorted([*serializer.data])
        )


class TestLightweightNotificationSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_data = {
            "id": 1,
            "verb": "Hello",
            "timestamp": timezone.localtime(),
        }

        cls.valid_key = [
            "id",
            "verb",
            "created_at",
        ]

    def test_to_representation(self):
        serializer = LightweightNotificationSerializer(self.valid_data)

        self.assertListEqual(self.valid_key, [*serializer.data])
