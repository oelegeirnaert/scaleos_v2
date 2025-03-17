from factory import SubFactory
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


class ReservationFactory(
    DjangoModelFactory[reservation_models.Reservation],
):
    class Meta:
        model = reservation_models.Reservation


class ReservationLineFactory(
    DjangoModelFactory[reservation_models.ReservationLine],
):
    reservation = SubFactory(ReservationFactory)

    class Meta:
        model = reservation_models.ReservationLine


class EventReservationSettingsFactory(
    DjangoModelFactory[reservation_models.EventReservationSettings],
):
    class Meta:
        model = reservation_models.EventReservationSettings
