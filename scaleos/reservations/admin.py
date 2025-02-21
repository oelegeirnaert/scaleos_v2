from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin

from scaleos.reservations import models as reservation_models


class ReservationLineInlineAdmin(admin.TabularInline):
    model = reservation_models.ReservationLine
    extra = 0
    show_change_link = True
    readonly_fields = ["total_price"]


class EventReservationInlineAdmin(admin.TabularInline):
    model = reservation_models.EventReservation
    extra = 0
    show_change_link = True
    readonly_fields = ["total_price"]


@admin.register(reservation_models.EventReservation)
class EventReservationAdmin(PolymorphicChildModelAdmin):
    base_model = reservation_models.EventReservation  # Explicitly set here!
    # define custom features here
    readonly_fields = [
        "created_on",
        "modified_on",
        "public_key",
        "total_price",
        "total_amount",
    ]
    inlines = [ReservationLineInlineAdmin]


@admin.register(reservation_models.Reservation)
class ReservationAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin):
    base_model = reservation_models.Reservation
    child_models = [
        reservation_models.Reservation,  # Delete once a submodel has been added.
        reservation_models.EventReservation,
    ]
    list_filter = [PolymorphicChildModelFilter]
    readonly_fields = [
        "created_on",
        "modified_on",
        "public_key",
        "total_price",
        "total_amount",
    ]
    list_display = [
        "__str__",
        "user",
        "created_on",
        "finished_on",
        "total_price",
        "total_amount",
        "verified_email",
    ]


@admin.register(reservation_models.ReservationLine)
class ReservationLineAdmin(admin.ModelAdmin):
    readonly_fields = ["total_price", "minimum_amount", "maximum_amount"]
