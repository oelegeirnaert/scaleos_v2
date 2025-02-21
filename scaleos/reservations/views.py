import logging

from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from scaleos.reservations import models as reservation_models

logger = logging.getLogger(__name__)


@cache_page(60 * 15)
def reservation(request, reservation_public_key):
    context = {}
    reservation = get_object_or_404(
        reservation_models.Reservation,
        public_key=reservation_public_key,
    )
    context["reservation"] = reservation
    template_used = reservation.page_template
    logger.debug("Templated used: %s", template_used)
    return render(
        request,
        template_used,
        context,
    )


@cache_page(60 * 15)
def eventreservation(request, eventreservation_public_key):
    context = {}
    eventreservation = get_object_or_404(
        reservation_models.EventReservation,
        public_key=eventreservation_public_key,
    )
    context["eventreservation"] = eventreservation
    template_used = eventreservation.page_template
    logger.debug("Templated used: %s", template_used)
    return render(
        request,
        template_used,
        context,
    )
