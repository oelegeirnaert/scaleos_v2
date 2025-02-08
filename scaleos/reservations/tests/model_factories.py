from factory.django import DjangoModelFactory

from scaleos.reservations import models as reservation_models


class BrunchReservationFactory(
    DjangoModelFactory[reservation_models.BrunchReservation],
):
    class Meta:
        model = reservation_models.BrunchReservation
