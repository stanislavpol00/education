from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.signals import reset_password_token_created

import constants
from libs.messaging.email import Mailer

from ..models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def creating_user(sender, instance, created, **kwargs):
    if created:
        user_type = constants.UserType.EDUCATOR_SHADOW
        if instance.is_staff:
            user_type = constants.UserType.ADMIN

        Profile.objects.create(
            user=instance,
            usertype=user_type,
        )


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    password_reset_link = reset_password_token.user.get_password_reset_link(
        reset_password_token
    )

    Mailer.send_html_mail(
        subject=_("Your password reset request!"),
        to_email=reset_password_token.user.email,
        template_name="password_reset.html",
        context={
            "password_reset_link": password_reset_link,
        },
    )
