import logging

from django.contrib.auth.decorators import login_required

from scaleos.reservations import models as reservation_models
from scaleos.shared.views import page_or_list_page

logger = logging.getLogger(__name__)


@login_required
def reservation(request, reservation_public_key=None):
    active_organization_id = request.session.get("active_organization_id", None)
    alternative_resultset = None
    if active_organization_id and request.user.is_organization_owner(
        active_organization_id,
    ):
        alternative_resultset = reservation_models.Reservation.objects.filter(
            organization_id=active_organization_id,
        )

    return page_or_list_page(
        request,
        reservation_models.Reservation,
        reservation_public_key,
        alternative_resultset=alternative_resultset,
    )


@login_required
def eventreservation(request, eventreservation_public_key):
    return page_or_list_page(
        request,
        reservation_models.EventReservation,
        eventreservation_public_key,
    )


@login_required
def guestinvite(request, guestinvite_public_key=None):
    return page_or_list_page(
        request,
        reservation_models.GuestInvite,
        guestinvite_public_key,
    )
