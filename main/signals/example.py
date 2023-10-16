from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

import constants
from libs.websocket import ExampleNotificationWebsocket
from tasks import notification

from ..models import Example, StudentExample, StudentTip


@receiver(post_save, sender=Example)
def post_updating_example(sender, instance, created, **kwargs):
    # to fix the old UI
    # TODOs: remove after new UI is ready
    if instance.episode_id:
        student_example, created = StudentExample.objects.get_or_create(
            student_id=instance.episode.student_id,
            example_id=instance.id,
            episode_id=instance.episode_id,
            added_by_id=instance.added_by_id,
            defaults={"reason": constants.StudentExample.REASON_EPISODE},
        )
        if not created:
            # make sure it will call signal
            student_example.save(update_fields=["updated_at"])

    # Notifications
    if created:
        notification.create_notifications.delay(
            instance.generate_example_creation_notification()
        )
        if instance.tip_id:
            ExampleNotificationWebsocket.send_example_notification_to_tip_owner(
                instance, updated=False
            )
            notification.create_notifications.delay(
                instance.generate_attach_tip_notifications(instance.tip)
            )
    else:
        notification.create_notifications.delay(
            instance.generate_example_updating_notification()
        )


@receiver(pre_save, sender=Example)
def example_pre_save(sender, instance, **kwargs):
    if instance.id is not None:
        old_example = Example.objects.get(id=instance.id)
        if old_example.tip_id != instance.tip_id:
            ExampleNotificationWebsocket.send_example_notification_to_tip_owner(
                instance, updated=True
            )
            if instance.tip_id:
                notification.create_notifications.delay(
                    instance.generate_attach_tip_notifications(instance.tip)
                )
            else:
                notification.create_notifications.delay(
                    instance.generate_detach_tip_notifications(old_example.tip)
                )

        if (
            instance.tip_id
            and instance.episode_id
            and old_example.tip_id != instance.tip_id
        ):
            StudentTip.objects.filter(
                student_id=instance.episode.student_id, tip_id=instance.tip_id
            ).update(last_used_at=timezone.localtime())
    else:
        if instance.episode_id and instance.tip_id:
            StudentTip.objects.filter(
                student_id=instance.episode.student_id, tip_id=instance.tip_id
            ).update(last_used_at=timezone.localtime())
