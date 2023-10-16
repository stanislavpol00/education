from django.db.models.signals import post_save
from django.dispatch import receiver

from tasks import notification

from ..models import TipRating


@receiver(post_save, sender=TipRating)
def tip_rating_post_save(sender, instance, created, **kwargs):
    if created:
        notification.create_notifications.delay(
            instance.generate_tip_rating_creation_notification()
        )
