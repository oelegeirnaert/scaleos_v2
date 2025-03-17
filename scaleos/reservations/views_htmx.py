import logging

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache

from scaleos.events import models as event_models
from scaleos.reservations import models as reservation_models
from scaleos.shared import views_htmx as shared_htmx
from scaleos.shared.views_htmx import htmx_response

logger = logging.getLogger("scaleos")

EVENT_RESERVATION_ID_KEY = "event_reservation_id"


@never_cache
def event_reservation(request, event_public_key):
    logger.setLevel(logging.DEBUG)
    shared_htmx.do_htmx_get_checks(request)
    event = get_object_or_404(event_models.Event, public_key=event_public_key)

    if reservation_models.EventReservation.objects.filter(
        event_id=event.pk,
        user_id=request.user.pk,
    ).exists():
        return HttpResponse(
            _("you already made a reservation for this event").capitalize(),
        )

    if event.reservations_are_closed:
        return HttpResponse(
            _(
                "sorry, the resservations for this event are already closed",
            ).capitalize(),
        )

    event_reservation_id = request.session.get(EVENT_RESERVATION_ID_KEY, None)
    logger.debug("creating a new reservation for this session")
    event_reservation, created = (
        reservation_models.EventReservation.objects.get_or_create(
            id=event_reservation_id,
        )
    )
    if created:
        request.session[EVENT_RESERVATION_ID_KEY] = event_reservation.pk

    event_reservation.event_id = event.pk
    event_reservation.save()

    try:
        applicable_prices = event.current_price_matrix.prices.all()
        applicable_prices_ids = applicable_prices.values_list("id", flat=True)
        already_present_prices = event_reservation.lines.all().values_list(
            "price_matrix_item_id",
            flat=True,
        )

        logger.debug("Applicable price ids: %s", applicable_prices_ids)
        event_reservation.lines.all().exclude(
            price_matrix_item_id__in=applicable_prices_ids,
        ).delete()
        logger.debug("Already present: %s", already_present_prices)
        for price_matrix_item in applicable_prices:
            if price_matrix_item.id not in already_present_prices:
                logger.debug(
                    "%s not present in %s",
                    price_matrix_item.id,
                    already_present_prices,
                )
                reservation_models.ReservationLine.objects.create(
                    reservation_id=event_reservation.pk,
                    price_matrix_item_id=price_matrix_item.pk,
                    amount=0,
                )

    except Exception as e:  # noqa: BLE001
        logger.info(e)
        event_reservation.lines.all().delete()
        logger.info("No pricing set for event %s", event.pk)

    template_used = event_reservation.detail_template
    logger.debug("Template used: %s", template_used)
    html_fragment = get_template(template_used).render(
        context={
            "event_reservation": event_reservation,
        },
        request=request,
    )
    return htmx_response(request, html_fragment)


def update_reservation_line(request, reservationline_public_key):
    logger.setLevel(logging.DEBUG)
    shared_htmx.do_htmx_post_checks(request)

    event_reservation_id = request.session.get(EVENT_RESERVATION_ID_KEY, None)
    logger.debug("Searching for event reservation: %s", event_reservation_id)
    get_object_or_404(
        reservation_models.EventReservation,
        id=event_reservation_id,
    )
    logger.debug("Event reservation found")

    logger.debug(
        "Searching for reservation line with public key: %s",
        reservationline_public_key,
    )
    reservationline = get_object_or_404(
        reservation_models.ReservationLine,
        public_key=reservationline_public_key,
    )
    logger.info(list(request.POST.items()))
    the_amount = request.POST.get(f"{reservationline.html_public_key}_amount", 0)
    logger.info("The amount we got: %s", the_amount)
    if isinstance(the_amount, str) and len(the_amount) == 0:
        the_amount = 0

    try:
        the_amount = int(the_amount)
    except ValueError:
        logger.warning("We cannot convert '%s' to an integer", the_amount)
        the_amount = 0

    logger.debug("Update amount to: %s", the_amount)
    if the_amount < 0:
        logger.info("The amount is lower than ZERO, force setting it to 0")
        the_amount = 0
    reservationline.amount = the_amount
    reservationline.save()

    template_used = reservationline.detail_template
    logger.debug("Template used: %s", template_used)
    html_fragment = get_template(template_used).render(
        context={
            "reservationline": reservationline,
        },
        request=request,
    )
    logger.debug("Return the response")
    return htmx_response(request, html_fragment)


def event_reservation_total_price(request, eventreservation_public_key):
    form_state = "disabled style=opacity:0.5;"

    def return_it(msg):
        html_fragment = get_template(
            "reservations/eventreservation/confirmation.html",
        ).render(
            context={
                "event_reservation": event_reservation,
                "message": msg,
                "amount": total_people_for_reservation,
                "price": event_reservation.total_price,
                "form_state": form_state,
            },
            request=request,
        )
        return HttpResponse(html_fragment)

    logger.info("The Public Key: %s", eventreservation_public_key)
    event_reservation = get_object_or_404(
        reservation_models.EventReservation,
        public_key=eventreservation_public_key,
    )

    reservation_settings = event_reservation.event.applicable_reservation_settings
    logger.debug(reservation_settings)
    total_people_for_reservation = event_reservation.total_amount
    if reservation_settings:
        mimimum_people = reservation_settings.minimum_persons_per_reservation
        logger.debug("minimum people in reservation: %s", mimimum_people)
        if total_people_for_reservation < mimimum_people:
            msg = _(
                f"you need at least {mimimum_people} persons to make this reservation".capitalize(),  # noqa: E501
            )
            return return_it(msg)

        maximum_people = reservation_settings.maximum_persons_per_reservation
        logger.debug("maximum people in reservation: %s", maximum_people)
        if total_people_for_reservation > maximum_people:
            msg = _(
                f"you need at most {maximum_people} persons to make this reservation".capitalize(),  # noqa: E501
            )
            return return_it(msg)

    form_state = ""
    msg = _("total price for %(amount)s persons: %(price)s".capitalize()) % {
        "amount": total_people_for_reservation,
        "price": event_reservation.total_price,
    }
    return return_it(msg)


def finish_reservation(request, reservation_public_key):
    min_email_length = 5
    logger.setLevel(logging.DEBUG)
    shared_htmx.do_htmx_post_checks(request)
    confirmation_email_address = request.POST.get("confirmation_email_address", "")
    if len(confirmation_email_address) < min_email_length:
        return HttpResponse(_("this is not a valid email address"))

    reservation = get_object_or_404(
        reservation_models.Reservation,
        public_key=reservation_public_key,
    )

    try:
        reservation.finish(
            request=request,
            confirmation_email_address=confirmation_email_address,
        )
    except ValidationError as e:
        return HttpResponse(str(e).capitalize())

    if isinstance(reservation, reservation_models.Reservation):
        request.session[EVENT_RESERVATION_ID_KEY] = None
    return HttpResponse(_("reservation requested"))


def organization_confirm_reservation(request):
    shared_htmx.do_htmx_post_checks(request)
    reservation_public_key = request.POST.get("reservation_public_key", None)
    if reservation_public_key is None:
        logger.error("no reservation public key in post request")
        return HttpResponse(_("we cannot confirm this reservation"))
    reservation = get_object_or_404(
        reservation_models.Reservation,
        public_key=reservation_public_key,
    )
    reservation.organization_confirm()
    return HttpResponse(_("reservation confirmed"))


def requester_confirm_reservation(request):
    shared_htmx.do_htmx_post_checks(request)
    reservation_public_key = request.POST.get("reservation_public_key", None)
    if reservation_public_key is None:
        logger.error("no reservation public key in post request")
        return HttpResponse(_("we cannot confirm this reservation"))
    reservation = get_object_or_404(
        reservation_models.Reservation,
        public_key=reservation_public_key,
    )
    reservation.requester_confirm()
    return HttpResponse(_("reservation confirmed"))
