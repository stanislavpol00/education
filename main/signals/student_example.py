from django.db.models.signals import post_save
from django.dispatch import receiver

import constants
from tasks import notification

from ..models import StudentExample, StudentTip, Task


@receiver(post_save, sender=StudentExample)
def updating_studentexample(sender, instance, created, **kwargs):
    if created and instance.example.tip:
        st, scre = StudentTip.objects.get_or_create(
            student=instance.student,
            tip=instance.example.tip,
            defaults={
                "added_by_id": instance.added_by_id,
            },
        )

        tasks = Task.objects.filter(
            tip=st.tip,
            student=st.student,
            user=instance.added_by,
            task_type=constants.TaskType.EXAMPLE,
        )
        tasks.delete()
        notification.create_notifications.delay(
            instance.generate_student_example_creation_notification()
        )

    elif instance.example.tip:
        st, scre = StudentTip.objects.update_or_create(
            student=instance.student,
            tip=instance.example.tip,
            defaults={
                "added_by_id": instance.added_by_id,
            },
        )
