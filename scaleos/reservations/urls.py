from django.urls import path

from scaleos.reservations import views as reservation_views

app_name = "reservations"
urlpatterns = [
    path(
        "",
        view=reservation_views.reservation,
        name="reservation",
    ),
    path(
        "<str:reservation_public_key>/",
        view=reservation_views.reservation,
        name="reservation",
    ),
    path(
        "event/<str:eventreservation_public_key>/",
        view=reservation_views.eventreservation,
        name="eventreservation",
    ),
    path(
        "event/guest/invite/",
        view=reservation_views.guestinvite,
        name="guestinvite",
    ),
    path(
        "event/guest/invite/<str:guestinvite_public_key>/",
        view=reservation_views.guestinvite,
        name="guestinvite",
    ),
]
