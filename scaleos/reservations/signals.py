from allauth.account.signals import email_confirmed
from django.conf import settings
from django.dispatch import receiver
from templated_email import send_templated_mail


@receiver(email_confirmed)
def send_post_confirmation_email(request, email_address, **kwargs):
    """Send a follow-up email after email confirmation."""
    user = email_address.user

    send_templated_mail(
        template_name="reservation/created.email",  # Name of the email template
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        context={
            "user": user,
            "site_name": "ScaleOS",
            "support_email": "support@example.com",
            "subject": "Your email is Confirmed 🎉",
        },
    )
