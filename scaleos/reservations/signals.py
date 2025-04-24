import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

from scaleos.reservations.models import EventReservation

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=EventReservation)
def set_event_reservation_expiry_datetime(sender, instance, **kwargs):
    logger.debug("Setting the expiry datetime %s", instance.pk)

    if instance.event and hasattr(instance.event, "ending_on"):
        instance.expired_on = instance.event.ending_on
