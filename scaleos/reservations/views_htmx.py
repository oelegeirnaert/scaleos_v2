import logging

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache

from scaleos.events import models as event_models
from scaleos.organizations.context_processors import organization_context
from scaleos.reservations import models as reservation_models
from scaleos.reservations.functions import get_organization_id_from_reservation
from scaleos.shared import views_htmx as shared_htmx
from scaleos.shared.decorators import limit_unauthenticated_submissions
from scaleos.shared.functions import valid_email_address
from scaleos.shared.mixins import ITS_NOW
from scaleos.shared.views_htmx import htmx_response

logger = logging.getLogger("scaleos")

EVENT_RESERVATION_ID_KEY = "event_reservation_id"


@never_cache
def event_reservation(request, event_public_key):
    shared_htmx.do_htmx_get_checks(request)
    event = get_object_or_404(event_models.Event, public_key=event_public_key)
    the_context = organization_context(request)

    logged_in_user = request.user.is_authenticated
    logger.debug("Is the user logged in? %s", logged_in_user)

    is_organization_employee = the_context.get("is_organization_employee", False)
    logger.debug("Is it an organization employee? %s", is_organization_employee)

    if not is_organization_employee:
        logger.debug("It is not an employee, so do additional checks")
        user_aleady_made_a_reservation = (
            reservation_models.EventReservation.objects.filter(
                event_id=event.pk,
                user_id=request.user.pk,
            ).exists()
        )
        logger.debug(
            "Does the user already made a reservation? %s",
            user_aleady_made_a_reservation,
        )

        if logged_in_user and user_aleady_made_a_reservation:
            msg = _("you already made a reservation for this event")
            logger.debug(msg)
            return HttpResponse(msg.capitalize())

        if hasattr(event, "reservations_are_closed") and event.reservations_are_closed:
            msg = _("sorry, the reservations for this event are already closed")
            logger.debug(msg)
            return HttpResponse(msg.capitalize())

    logger.debug("Getting event reservation from the session...")
    event_reservation_id = request.session.get(EVENT_RESERVATION_ID_KEY, None)
    logger.debug("Getting event reservation from session: %s", event_reservation_id)
    event_reservation, created = (
        reservation_models.EventReservation.objects.get_or_create(
            id=event_reservation_id,
        )
    )
    if created:
        logger.debug("creating a new reservation for this session")
        if logged_in_user:
            event_reservation.user_id = request.user.pk
        request.session[EVENT_RESERVATION_ID_KEY] = event_reservation.pk

    if logged_in_user:
        event_reservation.modified_by_id = request.user.pk

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
    logger.debug(list(request.POST.items()))
    shared_htmx.do_htmx_post_checks(request)
    logger.debug("ready with htmx checks")

    logger.debug("Getting event reservation from the session...")
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
    reservationline.save(update_fields=["amount"])

    template_used = reservationline.detail_template
    logger.debug("Template used: %s", template_used)
    logger.debug("The request is %s", request)
    logger.debug("The reservationline is %s", reservationline)

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
    total_people_for_reservation = 0

    def return_it(msg):
        html_fragment = get_template(
            "reservations/eventreservation/confirmation.html",
        ).render(
            context={
                "event_reservation": event_reservation,
                "message": msg,
                "amount": total_people_for_reservation,
                "price": event_reservation.get_total_price(),
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

    if event_reservation.event is None:
        msg = _("this event reservation has no event assigned")
        return return_it(msg)

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
        "price": event_reservation.get_total_price(),
    }
    return return_it(msg)


@limit_unauthenticated_submissions(
    form_id="public_reservation_finish",
    limit=5,
    timeout=3600,
)
def finish_reservation(request, reservation_public_key):
    shared_htmx.do_htmx_post_checks(request)

    reservation = get_object_or_404(
        reservation_models.Reservation,
        public_key=reservation_public_key,
    )

    if reservation.finished_on:
        msg = _("this reservation has already been finished")
        request.session[EVENT_RESERVATION_ID_KEY] = None
        logger.warning(msg)
        return HttpResponse(msg)

    active_organization_id = request.session.get("active_organization_id", None)
    if active_organization_id is None:
        active_organization_id = get_organization_id_from_reservation(reservation)

    if active_organization_id is None:
        msg = _("we don't know to which organization this reservation belongs")
        reservation_models.InvalidReservation.objects.create(
            reservation_id=reservation.pk,
            reason=reservation_models.InvalidReservation.InvalidReason.NO_ACTIVE_ORGANIZATION,
            additional_info=msg,
        )
        logger.error(msg)
        return HttpResponse(msg)

    confirmation_email_address = request.POST.get("confirmation_email_address", "")
    valid_email, invalid_reason = valid_email_address(confirmation_email_address)
    if not valid_email:
        reservation_models.InvalidReservation.objects.create(
            reservation_id=reservation.pk,
            reason=reservation_models.InvalidReservation.InvalidReason.INVALID_EMAIL,
            additional_info=invalid_reason,
        )
        logger.error(invalid_reason)
        logger.debug("returning invalid reason")
        return HttpResponse(invalid_reason)

    if isinstance(reservation, reservation_models.EventReservation):
        if reservation.total_amount == 0:
            msg = _("for an event reservation, you need at least one person")
            logger.warning(msg)
            raise ValidationError(msg)

    reservation.customer_comment = request.POST.get("customer_comment", "")
    reservation.customer_telephone = request.POST.get("customer_telephone", "")
    reservation.organization_id = active_organization_id

    try:
        reservation.add_user(request, confirmation_email_address)
        reservation.requester_auto_confirm(request)
        reservation.organization_auto_confirm()

        reservation.finished_on = ITS_NOW
        reservation.save()

    except ValidationError as e:
        return HttpResponse(str(e).capitalize())

    if isinstance(reservation, reservation_models.Reservation):
        request.session[EVENT_RESERVATION_ID_KEY] = None

    if reservation.is_in_waiting_list:
        return HttpResponse(
            _("reservation requested, but your are on our waiting list").capitalize(),
        )

    return HttpResponse(_("reservation requested").capitalize())


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

def reservation_updates(request, reservation_public_key):
    shared_htmx.do_htmx_get_checks(request)
    reservationupdate_list = reservation_models.ReservationUpdate.objects.filter(
        reservation__public_key=reservation_public_key,
    ).order_by("-created_on")


    template_used = "row_list.html"
    logger.debug("Template used: %s", template_used)
    row_list_title = _("reservation updates")
    html_fragment = get_template(template_used).render(
        context={
            "rows": reservationupdate_list,
            "row_list_title": row_list_title,
        },
        request=request,
    )
    return htmx_response(request, html_fragment)

