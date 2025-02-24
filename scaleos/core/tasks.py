import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from templated_email import send_templated_mail

from scaleos.reservations import models as reservation_models
from scaleos.shared.mixins import ITS_NOW

logger = logging.getLogger(__name__)


def send_custom_templated_email(request, emailconfirmation, reservation=None):
    """Send email confirmation using django_templated_email."""
    logger.debug(
        "Custom send_custom_templated_email is being called!",
    )
    logger.debug("🚀 Request: %s", request)
    logger.debug("🚀 Email Confirmation: %s", emailconfirmation)

    site_name = "ScaleOS.net"
    try:
        current_site = Site.objects.get_current()
        site_name = current_site.domain
    except Exception:  # noqa: BLE001
        logger.info("We cannot get the domain from the current site.")

    user = emailconfirmation.email_address.user
    email = emailconfirmation.email_address.email

    # Generate confirmation URL
    confirmation_url = "http://ScaleOS.net"
    if request:
        confirmation_url = request.build_absolute_uri(
            reverse("account_confirm_email", args=[emailconfirmation.key]),
        )

    if isinstance(reservation, reservation_models.Reservation):
        # Send reservation email
        send_templated_mail(
            template_name="reservation/email_confirmation_message.email",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            context={
                "user": user,
                "confirmation_url": confirmation_url,
                "reservation": reservation,
                "site_name": site_name,
            },
        )
    else:
        # Send normal email
        send_templated_mail(
            template_name="account/email_confirmation_message.email",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            context={
                "user": user,
                "confirmation_url": confirmation_url,
                "reservation": reservation,
                "site_name": site_name,
            },
        )

    if emailconfirmation.sent is None:
        emailconfirmation.sent = ITS_NOW
        emailconfirmation.save()
