import logging

from scaleos.reservations import models as reservation_models

logger = logging.getLogger(__name__)


def get_organization_from_reservation(reservation):
    logger.setLevel(logging.DEBUG)
    logger.debug("Trying to get the organization from the reservation")
    if isinstance(reservation, reservation_models.EventReservation):
        logger.debug("Its an event reservation")
        if hasattr(reservation.event, "concept"):
            logger.debug("It has a concept attribute")
            if reservation.event.concept and hasattr(
                reservation.event.concept,
                "organizer",
            ):
                logger.debug("It has an organization attribute")
                return reservation.event.concept.organizer_id
        if hasattr(reservation.event, "organization"):
            return reservation.event.organization.pk

    logger.warning("We cannot get the organization from the reservation")
    return None
