import logging

from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver

from scaleos.reservations import models as reservation_models

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@receiver(pre_save, sender=reservation_models.EventReservation)
def set_event_reservation_expiry_datetime(sender, instance, **kwargs):
    logger.debug(
        "Setting the expiry datetime to the event reservation with pk: %s", instance.pk,
    )

    if instance.event and hasattr(instance.event, "ending_on"):
        instance.expired_on = instance.event.ending_on

    if instance.event and hasattr(instance.event, "starting_at"):
        instance.start = instance.event.starting_at

    if instance.event and hasattr(instance.event, "ending_on"):
        instance.end = instance.event.ending_on


def register_signals_for_all_reservation_update_subclasses():
    for subclass in reservation_models.ReservationUpdate.__subclasses__():
        post_save.connect(
            update_confirmation_moment_signal, sender=subclass, weak=False,
        )


def update_confirmation_moment_signal(sender, instance, **kwargs):
    logger.debug("Updating confirmation moment via the signal")
    instance.reservation.update_confirmation_moment()


@receiver(post_save, sender=reservation_models.Reservation)
@receiver(post_save, sender=reservation_models.EventReservation)
def set_update_allow_requester_updates_until_datetime(sender, instance, **kwargs):
    logger.info("Signal to set the allowed requester updates datetime")
    instance.set_allow_requester_updates_until_datetime()
