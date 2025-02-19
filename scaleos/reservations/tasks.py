import logging

# myapp/utils.py
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

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

    # Send a welcome email
    subject = f"Please complete your reservation for {reservation}"
    message = """Hello,\n\nThank you for signing up!
    Please verify your email to set your password."""
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [reservation.user.email]

    send_mail(subject, message, from_email, recipient_list)

    reservation.confirmation_mail_sent_on = ITS_NOW
    reservation.save()
    return True
