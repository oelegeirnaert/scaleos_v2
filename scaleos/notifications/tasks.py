import logging

from celery.exceptions import SoftTimeLimitExceeded
from django.core.exceptions import ObjectDoesNotExist

# myapp/utils.py
from config import celery_app
from scaleos.notifications import models as notification_models

logger = logging.getLogger()


# @app.task(queue='queue1')
@celery_app.task(bind=True, soft_time_limit=60 * 60, max_retries=3)  # in seconds
def prepare_notification_sending(self, notification_id):
    logger.debug(
        "We need to prepare the sending of the "
        "notifications from notification with ID: %s",
        notification_id,
    )

    try:
        # This will return the correct subclass!
        notification = notification_models.Notification.objects.get(id=notification_id)
        model_name = notification.verbose_name.upper()
        if hasattr(notification, "send"):
            logger.debug("[SEND %s] #%s", model_name, notification_id)
            notification.send()
        else:
            logger.warning(
                "[%s] has no SEND method, skipping #%s",
                model_name,
                notification_id,
            )

    except ObjectDoesNotExist:
        logger.exception("[ERROR] Notification with ID %s not found.", notification_id)

    except SoftTimeLimitExceeded:
        logger.warning("[TIMEOUT] Task exceeded soft time limit.")

    except Exception as e:
        logger.exception("[RETRY] Task failed, retrying...")
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1)) from e
