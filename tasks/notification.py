# -*- coding: utf-8 -*-
from celery import shared_task
from notifications.signals import notify

from libs.cache import ActivityCache


@shared_task
def create_notifications(notifications_info):
    unique_cache_users = set()

    for notification_info in notifications_info:
        notify.send(**notification_info)

        if notification_info.get("level") != "success":
            continue

        if not hasattr(notification_info["recipient"], "id"):
            continue

        unique_cache_users.add(notification_info["recipient"].id)

    for user_id in unique_cache_users:
        ActivityCache.refresh(user_id)
