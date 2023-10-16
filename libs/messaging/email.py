from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


class Mailer:
    @staticmethod
    def send_html_mail(subject, to_email, template_name, context):
        msg_html = render_to_string(template_name, context)
        email_message = EmailMessage(
            subject=subject,
            body=msg_html,
            from_email=settings.FROM_EMAIL,
            to=[to_email],
        )
        email_message.content_subtype = "html"
        email_message.send()
