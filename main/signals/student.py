from django.db.models.signals import post_save
from django.dispatch import receiver

from tasks import notification

from ..models import Student


@receiver(post_save, sender=Student)
def student_post_save(sender, instance, created, **kwargs):
    if created:
        notification.create_notifications.delay(
            instance.generate_student_creation_notification()
        )
