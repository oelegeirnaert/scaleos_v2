import logging

from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from scaleos.reservations import models as reservation_models

logger = logging.getLogger(__name__)


@cache_page(60 * 15)
def reservation(request, public_key):
    context = {}
    reservation = get_object_or_404(
        reservation_models.Event,
        public_key=public_key,
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
def eventreservation(request, public_key):
    context = {}
    reservation = get_object_or_404(
        reservation_models.Reservation,
        public_key=public_key,
    )
    context["reservation"] = reservation
    template_used = reservation.page_template
    logger.debug("Templated used: %s", template_used)
    return render(
        request,
        template_used,
        context,
    )
