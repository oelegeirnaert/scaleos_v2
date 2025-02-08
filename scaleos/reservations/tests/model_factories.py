from collections.abc import Sequence
from typing import Any

from factory import Faker
from factory import fuzzy
from factory import post_generation
from factory.django import DjangoModelFactory
import datetime


from scaleos.reservations import models as reservation_models


class BrunchReservationFactory(DjangoModelFactory[reservation_models.BrunchReservation]):
    class Meta:
        model = reservation_models.BrunchReservation