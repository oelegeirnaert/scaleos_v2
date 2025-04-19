from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from scaleos.events import models as event_models


class ConceptTranslationOptions(TranslationOptions):
    fields = ("name", "card_description")


translator.register(event_models.Concept, ConceptTranslationOptions)


class CustomerConceptTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.CustomerConcept, CustomerConceptTranslationOptions)


class EventTranslationOptions(TranslationOptions):
    fields = ("name", "card_description")


translator.register(event_models.Event, EventTranslationOptions)


class WeddingEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.WeddingEvent, WeddingEventTranslationOptions)


class BrunchEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.BrunchEvent, BrunchEventTranslationOptions)


class DanceEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.DanceEvent, DanceEventTranslationOptions)


class DinnerEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.DinnerEvent, DinnerEventTranslationOptions)


class ReceptionEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.ReceptionEvent, ReceptionEventTranslationOptions)


class BirthdayEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.BirthdayEvent, BirthdayEventTranslationOptions)


class TeamBuildingEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.TeamBuildingEvent, TeamBuildingEventTranslationOptions)


class BreakEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.BreakEvent, BreakEventTranslationOptions)


class PresentationEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.PresentationEvent, PresentationEventTranslationOptions)


class MeetingEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.MeetingEvent, MeetingEventTranslationOptions)


class LivePerformanceEventTranslationOptions(TranslationOptions):
    pass


translator.register(
    event_models.LivePerformanceEvent,
    LivePerformanceEventTranslationOptions,
)


class BreakfastEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.BreakfastEvent, BreakfastEventTranslationOptions)


class LunchEventTranslationOptions(TranslationOptions):
    pass


translator.register(event_models.LunchEvent, LunchEventTranslationOptions)
