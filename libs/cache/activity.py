from django.core.cache import cache
from notifications.models import Notification


class ActivityCache:
    LAST_ACTIVITIES_CACHE_KEY = "LAST_ACTIVITIES"
    LAST_ACTIVITY_CACHE_KEY = "LAST_ACTIVITY_{}"
    TIMEOUT = 60 * 60 * 24  # a day

    @classmethod
    def refresh(cls, user_id):
        cls.get_last_activity_by_user(user_id, refresh=True)
        cls.get_activities_by_user(user_id, refresh=True)

    @classmethod
    def get_last_activity_by_user(cls, user_id, refresh=False):
        key_name = cls.LAST_ACTIVITY_CACHE_KEY.format(user_id)

        value = cache.get(key_name)
        if value and not refresh:
            return value

        last_notification = (
            Notification.objects.filter(level="success")
            .filter(recipient_id=user_id)
            .order_by("-timestamp")
            .first()
        )

        if not last_notification:
            return None

        cache.set(key_name, last_notification.timestamp, timeout=cls.TIMEOUT)

        return last_notification.timestamp

    @classmethod
    def get_last_activities(cls):
        key_name = cls.LAST_ACTIVITIES_CACHE_KEY

        value = cache.get(key_name)
        if value:
            return value

        notifications = (
            Notification.objects.filter(level="success")
            .order_by(
                "recipient_id",
                "-timestamp",
            )
            .distinct(
                "recipient_id",
            )
            .values(
                "recipient_id",
                "timestamp",
            )
        )

        last_activities = {}
        for notification in notifications:
            recipient_id = notification["recipient_id"]
            timestamp = notification["timestamp"]
            last_activities[recipient_id] = [timestamp]

        cache.set(key_name, last_activities, timeout=cls.TIMEOUT)

        return last_activities

    @classmethod
    def get_user_activities(cls, user_ids, **kwargs):
        notifications = Notification.objects.filter(
            recipient_id__in=user_ids, level="success"
        )

        if kwargs.get("start_date"):
            notifications = notifications.filter(
                timestamp__gte=kwargs["start_date"]
            )

        if kwargs.get("end_date"):
            notifications = notifications.filter(
                timestamp__lt=kwargs["end_date"]
            )

        notifications = (
            notifications.order_by(
                "recipient_id",
                "action_object_object_id",
                "action_object_content_type_id",
                "-timestamp",
            )
            .distinct(
                "recipient_id",
                "action_object_object_id",
                "action_object_content_type_id",
            )
            .values(
                "recipient_id",
                "action_object_object_id",
                "action_object_content_type_id",
                "timestamp",
            )
            .order_by("recipient_id")
        )

        last_activities = {}
        for notification in notifications:
            recipient_id = notification["recipient_id"]
            action_object_type_id = notification[
                "action_object_content_type_id"
            ]
            action_object_id = notification["action_object_object_id"]
            timestamp = notification["timestamp"]

            if recipient_id not in last_activities:
                last_activities[recipient_id] = {}

            if action_object_type_id not in last_activities[recipient_id]:
                last_activities[recipient_id][action_object_type_id] = []
            last_activities[recipient_id][action_object_type_id].append(
                {int(action_object_id): timestamp}
            )

        return last_activities

    @classmethod
    def get_activities_by_user(cls, user_id, **kwargs):
        notifications = Notification.objects.filter(
            level="success", recipient_id=user_id
        )

        if kwargs.get("start_date"):
            notifications = notifications.filter(
                timestamp__gte=kwargs["start_date"]
            )

        if kwargs.get("end_date"):
            notifications = notifications.filter(
                timestamp__lt=kwargs["end_date"]
            )

        notifications = (
            notifications.order_by(
                "recipient_id",
                "action_object_object_id",
                "action_object_content_type_id",
                "-timestamp",
            )
            .distinct(
                "recipient_id",
                "action_object_object_id",
                "action_object_content_type_id",
            )
            .values(
                "action_object_object_id",
                "action_object_content_type_id",
                "timestamp",
            )
        )

        activities = {}
        for notification in notifications:
            action_object_type_id = notification[
                "action_object_content_type_id"
            ]
            action_object_id = notification["action_object_object_id"]
            timestamp = notification["timestamp"]

            if action_object_type_id not in activities:
                activities[action_object_type_id] = []
            activities[action_object_type_id].append(
                {int(action_object_id): timestamp}
            )

        return activities
