import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

from scaleos.reservations import models as event_models

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=event_models.EventReservation)
def set_event_reservation_expiry_datetime(sender, instance, **kwargs):
    logger.debug("Setting the expiry datetime %s", instance.pk)

    if instance.event and hasattr(instance.event, "ending_on"):
        instance.expired_on = instance.event.ending_on

    if instance.event and hasattr(instance.event, "starting_at"):
        instance.start = instance.event.starting_at

    if instance.event and hasattr(instance.event, "ending_on"):
        instance.end = instance.event.ending_on
