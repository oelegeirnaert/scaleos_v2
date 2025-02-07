from collections.abc import Sequence
from typing import Any

from factory import Faker, SubFactory
from factory import fuzzy
from factory import post_generation
from factory.django import DjangoModelFactory
import datetime


from scaleos.events import models as event_models


class BrunchConceptFactory(DjangoModelFactory[event_models.BrunchConcept]):

    class Meta:
        model = event_models.BrunchConcept

class BrunchEventFactory(DjangoModelFactory[event_models.BrunchEvent]):
    concept = SubFactory(BrunchConceptFactory)

    class Meta:
        model = event_models.BrunchEvent



