from celery import shared_task
from django.core.management import call_command


@shared_task
def delete_versions():
    call_command("deleterevisions", keep=10, verbosity=0)
