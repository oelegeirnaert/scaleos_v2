import datetime

from factory import LazyAttribute
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDate

from scaleos.events import models as event_models
from scaleos.shared.mixins import ITS_NOW


class EventFactory(DjangoModelFactory[event_models.Event]):
    class Meta:
        model = event_models.Event


class ConceptFactory(DjangoModelFactory[event_models.Concept]):
    class Meta:
        model = event_models.Concept


class SingleEventFactory(DjangoModelFactory[event_models.SingleEvent]):
    concept = SubFactory(ConceptFactory)
    starting_at = FuzzyDate(
        datetime.datetime(ITS_NOW.year, 1, 1, 13, 00),
        datetime.datetime(ITS_NOW.year, 12, 31, 20, 00),
    )
    ending_on = LazyAttribute(lambda obj: obj.starting_at + datetime.timedelta(hours=4))

    class Meta:
        model = event_models.SingleEvent


class ConceptPriceMatrixFactory(DjangoModelFactory[event_models.ConceptPriceMatrix]):
    concept = SubFactory(ConceptFactory)

    class Meta:
        model = event_models.ConceptPriceMatrix


class BrunchEventFactory(DjangoModelFactory[event_models.BrunchEvent]):
    concept = SubFactory(ConceptFactory)

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


class EventDuplicatorFactory(DjangoModelFactory[event_models.EventDuplicator]):
    event = SubFactory(SingleEventFactory)
    to_date = LazyAttribute(
        lambda obj: obj.event.starting_at + datetime.timedelta(days=20),
    )

    class Meta:
        model = event_models.EventDuplicator


class CustomerConceptFactory(DjangoModelFactory[event_models.CustomerConcept]):
    class Meta:
        model = event_models.CustomerConcept


class EventFloorFactory(DjangoModelFactory[event_models.EventFloor]):
    class Meta:
        model = event_models.EventFloor


class EventAttendeeFactory(DjangoModelFactory[event_models.EventAttendee]):
    class Meta:
        model = event_models.EventAttendee


class AttendeeRoleFactory(DjangoModelFactory[event_models.AttendeeRole]):
    class Meta:
        model = event_models.AttendeeRole


class BirthdayEventFactory(DjangoModelFactory[event_models.BirthdayEvent]):
    class Meta:
        model = event_models.BirthdayEvent


class WeddingEventFactory(DjangoModelFactory[event_models.WeddingEvent]):
    class Meta:
        model = event_models.WeddingEvent


class TeamBuildingEventFactory(DjangoModelFactory[event_models.TeamBuildingEvent]):
    class Meta:
        model = event_models.TeamBuildingEvent


class BreakEventFactory(DjangoModelFactory[event_models.BreakEvent]):
    class Meta:
        model = event_models.BreakEvent


class PresentationEventFactory(DjangoModelFactory[event_models.PresentationEvent]):
    class Meta:
        model = event_models.PresentationEvent


class MeetingEventFactory(DjangoModelFactory[event_models.MeetingEvent]):
    class Meta:
        model = event_models.MeetingEvent


class LivePerformanceEventFactory(
    DjangoModelFactory[event_models.LivePerformanceEvent],
):
    class Meta:
        model = event_models.LivePerformanceEvent


class BreakfastEventFactory(DjangoModelFactory[event_models.BreakfastEvent]):
    class Meta:
        model = event_models.BreakfastEvent


class LunchEventFactory(DjangoModelFactory[event_models.LunchEvent]):
    class Meta:
        model = event_models.LunchEvent


class EventUpdateFactory(DjangoModelFactory[event_models.EventUpdate]):
    event = SubFactory(EventFactory)

    class Meta:
        model = event_models.EventUpdate


class EventMessageFactory(DjangoModelFactory[event_models.EventMessage]):
    event = SubFactory(EventFactory)

    class Meta:
        model = event_models.EventMessage
