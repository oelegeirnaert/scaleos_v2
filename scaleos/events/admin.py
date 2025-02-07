from django.contrib import admin
from scaleos.events import models as event_models
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import PolymorphicChildModelAdmin, StackedPolymorphicInline, PolymorphicInlineSupportMixin

# Register your models here.
class EventInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """
    class BrunchInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.BrunchEvent

    class DinnerEventInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.DinnerEvent

    class DanceInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.DanceEvent

    model = event_models.SingleEvent
    child_inlines = (
        BrunchInlineAdmin,
        DinnerEventInlineAdmin,
        DanceInlineAdmin,
    )

@admin.register(event_models.WeddingConcept)
class WeddingConceptAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.WeddingConcept  # Explicitly set here!
    # define custom features here

@admin.register(event_models.BrunchConcept)
class BrunchConceptAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin):
    base_model = event_models.BrunchConcept  # Explicitly set here!
    # define custom features here
    inlines = [EventInlineAdmin]
    

@admin.register(event_models.DinnerAndDanceConcept)
class DinnerAndDanceConceptAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.DinnerAndDanceConcept  # Explicitly set here!
    # define custom features here

@admin.register(event_models.Concept)
class ConceptAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin):
    base_model = event_models.Concept
    child_models = [
        event_models.Concept,  # Delete once a submodel has been added.
        event_models.WeddingConcept,
        event_models.BrunchConcept,
        event_models.DinnerAndDanceConcept,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["name"]
    search_fields = ["name"]
    inlines = [EventInlineAdmin]

@admin.register(event_models.BrunchEvent)
class BrunchEventAdmin(PolymorphicChildModelAdmin):
    from scaleos.reservations.admin import BrunchReservationInlineAdmin
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here
    inlines = [BrunchReservationInlineAdmin]
    readonly_fields = ["free_spots", "free_percentage"]

@admin.register(event_models.ReceptionEvent)
class ReceptionEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here

@admin.register(event_models.DinnerEvent)
class DinnerEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here

@admin.register(event_models.DanceEvent)
class DanceEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here

@admin.register(event_models.SingleEvent)
class SingleEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.Event  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage"]

@admin.register(event_models.Event)
class EventAdmin(PolymorphicParentModelAdmin):
    base_model = event_models.Event
    child_models = [
        event_models.Event,  # Delete once a submodel has been added.
        event_models.SingleEvent,
        event_models.ReceptionEvent,
        event_models.BrunchEvent,
        event_models.DinnerEvent,
        event_models.DanceEvent,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["name"]
    search_fields = ["name"]



