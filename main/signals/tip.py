from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver

from libs.websocket import TipNotificationWebsocket
from tasks import notification

from ..models import Tip


@receiver(pre_save, sender=Tip)
def updating_tip(sender, instance, **kwargs):
    # To fix: null description raises error on the old ui
    if instance.description is None:
        instance.description = ""
    if instance.id is not None:
        old_tip = Tip.objects.get(id=instance.id)
        if not old_tip.marked_for_editing and instance.marked_for_editing:
            TipNotificationWebsocket.send_editing_notification_to_tip_owner(
                instance
            )

            notification.create_notifications.delay(
                instance.generate_set_tip_edit_mark_notification()
            )


@receiver(post_save, sender=Tip)
def tip_post_save(sender, instance, created, **kwargs):
    if created:
        notification.create_notifications.delay(
            instance.generate_tip_creation_notification()
        )
        if instance.linked_tips.values_list("id", flat=True):
            TipNotificationWebsocket.send_linked_tip_notification_to_linked_tip_owner(
                instance
            )
    else:
        notification.create_notifications.delay(
            instance.generate_tip_updating_notification()
        )


def linked_tips_changed(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        notification.create_notifications.delay(
            instance.generate_attach_tip_notifications(attached_tip_ids=pk_set)
        )
    if action == "pre_remove":
        notification.create_notifications.delay(
            instance.generate_detach_tip_notifications(detached_tip_ids=pk_set)
        )

    if isinstance(instance, Tip) and action == "post_add":
        TipNotificationWebsocket.send_linked_tip_notification_to_linked_tip_owner(
            instance
        )


m2m_changed.connect(linked_tips_changed, sender=Tip.linked_tips.through)
