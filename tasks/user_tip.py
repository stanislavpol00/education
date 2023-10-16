from celery import shared_task

import constants
from main.models import User


@shared_task
def dequeue_tips(number_of_tips=2):
    users = User.objects.by_role(role=constants.Role.EXPERIMENTAL_TEACHER)

    for user in users:
        user.dequeue_tips(number_of_tips)
