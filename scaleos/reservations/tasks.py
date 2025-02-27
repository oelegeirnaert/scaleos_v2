import logging

# myapp/utils.py
from django.conf import settings
from django.contrib.auth import get_user_model
from templated_email import send_templated_mail

from config import celery_app
from scaleos.reservations import models as reservation_models
from scaleos.shared.mixins import ITS_NOW

User = get_user_model()
logger = logging.getLogger()


# @app.task(queue='queue1')
@celery_app.task(bind=True, soft_time_limit=60 * 60)  # in seconds
def send_reservation_confirmation(self, reservation_id):
    logger.info(
        "We need to send a reservation confirmation for reservation: %s",
        reservation_id,
    )

    try:
        reservation = reservation_models.Reservation.objects.get(id=reservation_id)
    except reservation_models.Reservation.DoesNotExist:
        logger.info("The reservation does not exist")
        return False

    if reservation.confirmation_mail_sent_on:
        logger.info(
            "The confirmation mail for reservation %s is already sent on: %s",
            reservation.pk,
            reservation.confirmation_mail_sent_on,
        )
        return False

    # Send a welcome email
    user = reservation.user

    if user is None:
        logger.warning("The reservation %s has no user set.", reservation.pk)
        return False

    if user.email is None:  # pragma: no cover
        logger.warning(
            "The user of reservation %s has no email address set.",
            reservation.pk,
        )
        return False

    recipient_list = user.email

    send_templated_mail(
        template_name="reservation/reservation_confirmation_message.email",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_list],
        context={
            "user": user,
            "reservation": reservation,
            "site_name": "ScaleOS.net",
        },
    )

    reservation.confirmation_mail_sent_on = ITS_NOW
    reservation.save()
    return True
