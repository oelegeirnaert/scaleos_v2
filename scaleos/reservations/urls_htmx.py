from django.urls import path

from scaleos.reservations import views_htmx as vw_htmx

app_name = "reservations_htmx"

urlpatterns = [
    path(
        "event/<uuid:event_public_key>/",
        vw_htmx.event_reservation,
        name="event_reservation",
    ),
    path(
        "line/<uuid:reservationline_public_key>/",
        vw_htmx.update_reservation_line,
        name="update_reservation_line",
    ),
    path(
        "event/<uuid:eventreservation_public_key>/total/price/",
        vw_htmx.event_reservation_total_price,
        name="event_reservation_total_price",
    ),
    path(
        "<uuid:reservation_public_key>/finish/",
        vw_htmx.finish_reservation,
        name="finish_reservation",
    ),
    path(
        "organization/confirm/",
        vw_htmx.organization_confirm_reservation,
        name="organization_confirm_reservation",
    ),
]
