from django.urls import path

from scaleos.reservations import views as reservation_views

app_name = "reservations"
urlpatterns = [
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
]
