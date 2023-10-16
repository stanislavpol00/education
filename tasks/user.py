from celery import shared_task

from main.models import User


@shared_task
def update_last_login(username_or_email):
    user = User.objects.by_username_or_email(username_or_email)
    user.update_last_login()


@shared_task
def update_user_ip(username_or_email, user_ip):
    user = User.objects.by_username_or_email(username_or_email)
    user.update_user_ip(user_ip)
