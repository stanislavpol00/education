from django.db.models.signals import post_save
from django.dispatch import receiver

from libs.websocket import UserStudentMappingNotificationWebsocket

from ..models import UserStudentMapping


@receiver(post_save, sender=UserStudentMapping)
def user_student_mapping_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    UserStudentMappingNotificationWebsocket.send_assign_student_notification_to_mapped_user(
        instance
    )
