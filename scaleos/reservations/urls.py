from django.urls import path

from scaleos.reservations import views as reservation_views

app_name = "reservations"
urlpatterns = [
    path(
        "<str:public_key>/",
        view=reservation_views.reservation,
        name="reservation",
    ),
    path(
        "event/<str:public_key>/",
        view=reservation_views.eventreservation,
        name="eventreservation",
    ),
]
