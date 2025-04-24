import logging

from celery.exceptions import SoftTimeLimitExceeded

# myapp/utils.py
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from config import celery_app
from scaleos.reservations import models as reservation_models
from scaleos.shared.mixins import ITS_NOW

User = get_user_model()
logger = logging.getLogger()


@celery_app.task(bind=True, soft_time_limit=60 * 60, max_retries=3)
def send_reservation_update_notification(self, reservation_update_id):
    try:
        # This will return the correct subclass!
        update = reservation_models.ReservationUpdate.objects.get(
            id=reservation_update_id,
        )

        if hasattr(update, "send_notification_logic"):
            update.send_notification_logic()
        else:
            logger.info(
                "[NOTIFY] %s created for Reservation #%s...",
                update.model_name,
                update.reservation.id,
            )

    except ObjectDoesNotExist as odne:
        logger.exception(
            "[ERROR] ReservationUpdate with ID %s not found.",
            reservation_update_id,
        )
        raise self.retry(exc=odne, countdown=60 * (self.request.retries + 1)) from odne

    except SoftTimeLimitExceeded:
        logger.warning("[TIMEOUT] Task exceeded soft time limit.")

    except Exception as e:
        logger.exception("[RETRY] Task failed: {e}, retrying...")
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1)) from e


@celery_app.task(bind=True, soft_time_limit=60 * 60, max_retries=3)
def confirm_open_reservations_for_user(self, user_id):
    reservations = reservation_models.Reservation.objects.filter(
        Q(user_id=user_id) & (Q(expired_on__isnull=True) | Q(expired_on__gt=ITS_NOW)),
    )

    for reservation in reservations:
        reservation.requester_confirm()
        reservation.organization_auto_confirm()
