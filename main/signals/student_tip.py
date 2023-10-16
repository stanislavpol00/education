from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from libs.websocket import StudentTipNotificationWebsocket
from tasks import notification

from ..models import StudentTip


@receiver(pre_save, sender=StudentTip)
def student_tip_pre_save(sender, instance, **kwargs):
    if instance.id is None and instance.last_suggested_at is None:
        instance.last_suggested_at = timezone.localtime()


@receiver(post_save, sender=StudentTip)
def student_tip_post_save(sender, instance, created, **kwargs):
    if created:
        notification.create_notifications.delay(
            instance.generate_student_tip_creation_notification()
        )
        StudentTipNotificationWebsocket.send_student_tip_notification_to_mapped_users(
            instance
        )
