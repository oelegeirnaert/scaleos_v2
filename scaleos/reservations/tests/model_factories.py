from factory.django import DjangoModelFactory

from scaleos.reservations import models as reservation_models


class EventReservationFactory(
    DjangoModelFactory[reservation_models.EventReservation],
):
    class Meta:
        model = reservation_models.EventReservation


class BrunchReservationFactory(
    DjangoModelFactory[reservation_models.EventReservation],
):
    class Meta:
        model = reservation_models.EventReservation


class ReservationLineFactory(
    DjangoModelFactory[reservation_models.ReservationLine],
):
    class Meta:
        model = reservation_models.ReservationLine
