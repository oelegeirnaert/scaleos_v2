from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.events import models as event_models
from scaleos.shared.admin import LogInfoAdminMixin

# Register your models here.


class EventUpdateInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class EventUpdateInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.EventUpdate
        show_change_link = True

    class EventMessageInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.EventMessage
        show_change_link = True

    model = event_models.EventUpdate
    child_inlines = (
        EventUpdateInlineAdmin,
        EventMessageInlineAdmin,
    )


class ConceptPriceMatrixInlineAdmin(admin.TabularInline):
    model = event_models.ConceptPriceMatrix
    extra = 0
    show_change_link = True


class EventFloorInlineAdmin(admin.TabularInline):
    model = event_models.EventFloor
    extra = 0
    show_change_link = True


class AttendeeRoleInlineAdmin(admin.TabularInline):
    model = event_models.AttendeeRole
    extra = 0
    show_change_link = True


class EventAttendeeInlineAdmin(admin.TabularInline):
    model = event_models.EventAttendee
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

    class ReceptionInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.ReceptionEvent
        show_change_link = True

    class DinnerInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.DinnerEvent
        show_change_link = True

    class DanceInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.DanceEvent
        show_change_link = True

    class BirthdayInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.BirthdayEvent
        show_change_link = True

    class WeddingInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.WeddingEvent
        show_change_link = True

    class TeamBuildingInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.TeamBuildingEvent
        show_change_link = True

    class BreakInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.BreakEvent
        show_change_link = True

    class PresentationInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.PresentationEvent
        show_change_link = True

    class MeetingInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.MeetingEvent
        show_change_link = True

    class LivePerformanceInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.LivePerformanceEvent
        show_change_link = True

    class BreakfastInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.BreakfastEvent
        show_change_link = True

    class LunchInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.LunchEvent
        show_change_link = True

    class StayOverInlineAdmin(StackedPolymorphicInline.Child):
        model = event_models.StayOver
        show_change_link = True

    model = event_models.SingleEvent
    child_inlines = (
        WeddingInlineAdmin,
        BirthdayInlineAdmin,
        BreakfastInlineAdmin,
        LunchInlineAdmin,
        DinnerInlineAdmin,
        BrunchInlineAdmin,
        DanceInlineAdmin,
        ReceptionInlineAdmin,
        TeamBuildingInlineAdmin,
        MeetingInlineAdmin,
        BreakInlineAdmin,
        PresentationInlineAdmin,
        LivePerformanceInlineAdmin,
        StayOverInlineAdmin,
    )


@admin.register(event_models.EventDuplicator)
class EventDuplicatorAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = [EventInlineAdmin]
    actions = ["execute_duplicator"]

    @admin.action(
        description="execute selected duplicator",
    )
    def execute_duplicator(self, request, queryset):
        for duplicator in queryset:
            duplicator.duplicate()  # Call a method on each event
        self.message_user(request, "Selected events have been duplicated.")


@admin.register(event_models.Concept)
class ConceptAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin):
    base_model = event_models.Concept
    child_models = [
        event_models.Concept,  # Delete once a submodel has been added.
        event_models.CustomerConcept,
    ]
    list_filter = [PolymorphicChildModelFilter, "segment"]
    list_display = ["id", "name"]
    search_fields = ["name"]
    inlines = [ConceptPriceMatrixInlineAdmin, EventInlineAdmin]
    readonly_fields = ["public_key", "starting_at", "ending_on"]


@admin.register(event_models.CustomerConcept)
class CustomerConceptAdmin(
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
    LogInfoAdminMixin,
):
    base_model = event_models.Concept
    inlines = [*ConceptAdmin.inlines]
    readonly_fields = [*ConceptAdmin.readonly_fields]


@admin.register(event_models.BrunchEvent)
class BrunchEventAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin):
    from scaleos.reservations.admin import EventReservationAdmin

    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here

    readonly_fields = [
        "applicable_reservation_settings",
        "reservations_closed_on",
        "related_model_link",
        "free_spots",
        "free_percentage",
        "reserved_spots",
        "reserved_percentage",
        "over_reserved_spots",
        "slug",
        "current_price_matrix",
        "public_key",
    ]

    @admin.display(description=_("applicable reservation settings"))
    def related_model_link(self, obj):
        url = reverse(
            "admin:reservations_eventreservationsettings_change",
            args=[obj.applicable_reservation_settings.id],
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.applicable_reservation_settings.id,
        )


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
        event_models.BirthdayEvent,
        event_models.WeddingEvent,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["id", "name"]
    search_fields = ["name"]
    readonly_fields = ["warnings"]
    inlines = [EventFloorInlineAdmin]


@admin.register(event_models.SingleEvent)
class SingleEventAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin):
    base_model = event_models.Event  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage", "slug", "warnings"]
    list_display = ["__str__", "duplicator", "slug"]
    inlines = [EventAttendeeInlineAdmin, EventUpdateInlineAdmin, *EventAdmin.inlines]


@admin.register(event_models.ConceptPriceMatrix)
class ConceptPriceMatrixAdmin(admin.ModelAdmin):
    pass


@admin.register(event_models.EventFloor)
class EventFloorAdmin(admin.ModelAdmin):
    pass


@admin.register(event_models.EventAttendee)
class EventAttendeeAdmin(admin.ModelAdmin):
    inlines = [AttendeeRoleInlineAdmin]


@admin.register(event_models.AttendeeRole)
class AttendeeRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(event_models.BirthdayEvent)
class BirthdayEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage", "slug", "warnings"]
    inlines = [EventAttendeeInlineAdmin]


@admin.register(event_models.WeddingEvent)
class WeddingEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage", "slug", "warnings"]
    inlines = [EventAttendeeInlineAdmin]


@admin.register(event_models.TeamBuildingEvent)
class TeamBuildingEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage", "slug", "warnings"]
    inlines = [EventAttendeeInlineAdmin]


@admin.register(event_models.BreakEvent)
class BreakEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage", "slug", "warnings"]
    inlines = [EventAttendeeInlineAdmin]


@admin.register(event_models.PresentationEvent)
class PresentationEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage", "slug", "warnings"]
    inlines = [EventAttendeeInlineAdmin]


@admin.register(event_models.MeetingEvent)
class MeetingEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage", "slug", "warnings"]
    inlines = [EventAttendeeInlineAdmin]


@admin.register(event_models.LivePerformanceEvent)
class LivePerformanceEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage", "slug", "warnings"]
    inlines = [EventAttendeeInlineAdmin]


@admin.register(event_models.BreakfastEvent)
class BreakfastEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage", "slug", "warnings"]
    inlines = [EventAttendeeInlineAdmin]


@admin.register(event_models.LunchEvent)
class LunchEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here
    readonly_fields = ["free_spots", "free_percentage", "slug", "warnings"]
    inlines = [EventAttendeeInlineAdmin]


@admin.register(event_models.EventUpdate)
class EventUpdateAdmin(PolymorphicParentModelAdmin):
    base_model = event_models.EventUpdate
    child_models = [
        event_models.EventUpdate,  # Delete once a submodel has been added.
        event_models.EventMessage,
    ]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(event_models.EventMessage)
class EventMessageAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.EventUpdate  # Explicitly set here!
    # define custom features here
