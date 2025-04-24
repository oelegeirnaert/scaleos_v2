from celery import shared_task
from django.urls import reverse

from scaleos.notifications.models import UserNotification

from .models import User


@shared_task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@shared_task()
def create_confirmation_notification(request, emailconfirmation):
    if request:
        confirmation_url = request.build_absolute_uri(
            reverse("account_confirm_email", args=[emailconfirmation.key]),
        )
    user = emailconfirmation.email_address.user
    UserNotification.objects.create(
        button_link=confirmation_url,
        to_user=user,
    ).send()
    return True
