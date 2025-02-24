from factory import SubFactory
from factory.django import DjangoModelFactory

from scaleos.events import models as event_models


class EventFactory(DjangoModelFactory[event_models.Event]):
    class Meta:
        model = event_models.Event


class ConceptFactory(DjangoModelFactory[event_models.Concept]):
    class Meta:
        model = event_models.Concept


class SingleEventFactory(DjangoModelFactory[event_models.SingleEvent]):
    class Meta:
        model = event_models.SingleEvent


class ConceptPriceMatrixFactory(DjangoModelFactory[event_models.ConceptPriceMatrix]):
    concept = SubFactory(ConceptFactory)

    class Meta:
        model = event_models.ConceptPriceMatrix


class BrunchConceptFactory(DjangoModelFactory[event_models.BrunchConcept]):
    class Meta:
        model = event_models.BrunchConcept


class BrunchEventFactory(DjangoModelFactory[event_models.BrunchEvent]):
    concept = SubFactory(BrunchConceptFactory)

    class Meta:
        model = event_models.BrunchEvent


class ReceptionEventFactory(DjangoModelFactory[event_models.ReceptionEvent]):
    class Meta:
        model = event_models.ReceptionEvent


class DinnerEventFactory(DjangoModelFactory[event_models.DinnerEvent]):
    class Meta:
        model = event_models.DinnerEvent


class DanceEventFactory(DjangoModelFactory[event_models.DanceEvent]):
    class Meta:
        model = event_models.DanceEvent


class WeddingConceptFactory(DjangoModelFactory[event_models.WeddingConcept]):
    class Meta:
        model = event_models.WeddingConcept


class DinnerAndDanceConceptFactory(
    DjangoModelFactory[event_models.DinnerAndDanceConcept],
):
    class Meta:
        model = event_models.DinnerAndDanceConcept
