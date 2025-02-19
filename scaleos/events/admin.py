from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.events import models as event_models

# Register your models here.


class ConceptPriceMatrixInlineAdmin(admin.TabularInline):
    model = event_models.ConceptPriceMatrix
    extra = 0
    show_change_link = True


class EventInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class BrunchInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.BrunchEvent
        show_change_link = True

    class DinnerEventInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.DinnerEvent
        show_change_link = True

    class DanceInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.DanceEvent
        show_change_link = True

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
    inlines = [ConceptPriceMatrixInlineAdmin, EventInlineAdmin]
    readonly_fields = ["public_key"]


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
    inlines = [ConceptPriceMatrixInlineAdmin, EventInlineAdmin]


@admin.register(event_models.BrunchEvent)
class BrunchEventAdmin(PolymorphicChildModelAdmin):
    from scaleos.reservations.admin import EventReservationAdmin

    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here

    readonly_fields = [
        "free_spots",
        "free_percentage",
        "reserved_spots",
        "reserved_percentage",
        "over_reserved_spots",
        "slug",
        "current_price_matrix",
        "public_key",
    ]


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
    readonly_fields = ["free_spots", "free_percentage", "slug"]
    list_display = ["__str__", "slug"]


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


@admin.register(event_models.ConceptPriceMatrix)
class ConceptPriceMatrixAdmin(admin.ModelAdmin):
    pass
