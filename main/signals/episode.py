from django.db.models.signals import post_save
from django.dispatch import receiver

from libs.websocket import EpisodeNotificationWebsocket

from ..models import Episode


@receiver(post_save, sender=Episode)
def episode_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    EpisodeNotificationWebsocket.send_new_episode_notification(instance)
