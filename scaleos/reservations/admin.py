from django.contrib import admin
from scaleos.reservations import models as reservation_models
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import PolymorphicChildModelAdmin, StackedPolymorphicInline, PolymorphicInlineSupportMixin

class BrunchReservationInlineAdmin(admin.TabularInline):
    model = reservation_models.BrunchReservation
    extra = 0
    show_change_link = True
    readonly_fields = ["total_price"]

@admin.register(reservation_models.BrunchReservation)
class BrunchReservationAdmin(PolymorphicChildModelAdmin):
    base_model = reservation_models.BrunchReservation  # Explicitly set here!
    # define custom features here

@admin.register(reservation_models.Reservation)
class ReservationAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin):
    base_model = reservation_models.Reservation
    child_models = [
        reservation_models.Reservation,  # Delete once a submodel has been added.
        reservation_models.BrunchReservation,

    ]
    list_filter = [PolymorphicChildModelFilter]