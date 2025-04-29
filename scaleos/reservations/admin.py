from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.reservations import models as reservation_models
from scaleos.shared.admin import LogInfoAdminMixin
from scaleos.shared.admin import generic_relation_reverse_link


class ReservationLineInlineAdmin(admin.TabularInline):
    model = reservation_models.ReservationLine
    extra = 0
    show_change_link = True
    readonly_fields = ["total_price"]


class ReservationUpdateInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class OrganizationConfirmInlineAdmin(StackedPolymorphicInline.Child):
        model = reservation_models.OrganizationConfirm
        show_change_link = True
        readonly_fields = [*LogInfoAdminMixin.readonly_fields]

    class OrganizationCancelInlineAdmin(StackedPolymorphicInline.Child):
        model = reservation_models.OrganizationCancel
        show_change_link = True
        readonly_fields = [*LogInfoAdminMixin.readonly_fields]

    class OrganizationRefuseInlineAdmin(StackedPolymorphicInline.Child):
        model = reservation_models.OrganizationRefuse
        show_change_link = True
        readonly_fields = [*LogInfoAdminMixin.readonly_fields]

    class RequesterConfirmInlineAdmin(StackedPolymorphicInline.Child):
        model = reservation_models.RequesterConfirm
        show_change_link = True
        readonly_fields = [*LogInfoAdminMixin.readonly_fields]

    class RequesterCancelInlineAdmin(StackedPolymorphicInline.Child):
        model = reservation_models.RequesterCancel
        show_change_link = True
        readonly_fields = [*LogInfoAdminMixin.readonly_fields]

    class WaitingUserEmailConfirmationInlineAdmin(StackedPolymorphicInline.Child):
        model = reservation_models.WaitingUserEmailConfirmation
        show_change_link = True
        readonly_fields = [*LogInfoAdminMixin.readonly_fields]

    class InvalidReservationInlineAdmin(StackedPolymorphicInline.Child):
        model = reservation_models.InvalidReservation
        show_change_link = True
        readonly_fields = [*LogInfoAdminMixin.readonly_fields]

    class GuestInviteInlineAdmin(StackedPolymorphicInline.Child):
        model = reservation_models.GuestInvite
        show_change_link = True
        readonly_fields = [*LogInfoAdminMixin.readonly_fields]

    class OrganizationTemporarilyRejectedInlineAdmin(StackedPolymorphicInline.Child):
        model = reservation_models.OrganizationTemporarilyRejected
        show_change_link = True
        readonly_fields = [*LogInfoAdminMixin.readonly_fields]

    model = reservation_models.ReservationUpdate
    child_inlines = (
        OrganizationConfirmInlineAdmin,
        OrganizationCancelInlineAdmin,
        OrganizationRefuseInlineAdmin,
        OrganizationTemporarilyRejectedInlineAdmin,
        RequesterConfirmInlineAdmin,
        RequesterCancelInlineAdmin,
        GuestInviteInlineAdmin,
        WaitingUserEmailConfirmationInlineAdmin,
        InvalidReservationInlineAdmin,
    )


class EventReservationInlineAdmin(admin.TabularInline):
    model = reservation_models.EventReservation
    extra = 0
    show_change_link = True
    readonly_fields = ["total_price"]


@admin.register(reservation_models.EventReservation)
class EventReservationAdmin(
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
    LogInfoAdminMixin,
):
    base_model = reservation_models.Reservation  # Explicitly set here!
    # define custom features here
    readonly_fields = [
        "public_key",
        "total_amount",
        "total_payment_requests",
        "applicable_payment_settings_link",
        "latest_organization_update",
        "organization_status",
        "latest_requester_update",
        "requester_status",
        "is_confirmed",
        *LogInfoAdminMixin.readonly_fields,
    ]
    inlines = [ReservationUpdateInlineAdmin, ReservationLineInlineAdmin]
    autocomplete_fields = ["user", *LogInfoAdminMixin.autocomplete_fields]

    @admin.display(
        description=_("applicable payment settings link"),
    )
    def applicable_payment_settings_link(self, obj):
        return generic_relation_reverse_link(self, obj, "applicable_payment_settings")


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
        "total_amount",
        "applicable_payment_settings",
    ]
    list_display = [
        "__str__",
        "user",
        "created_on",
        "finished_on",
        "total_amount",
        "verified_email_address",
    ]
    inlines = [ReservationUpdateInlineAdmin]


@admin.register(reservation_models.ReservationUpdate)
class ReservationUpdateAdmin(
    PolymorphicInlineSupportMixin,
    PolymorphicParentModelAdmin,
):
    base_model = reservation_models.ReservationUpdate
    child_models = [
        reservation_models.ReservationUpdate,
        reservation_models.OrganizationConfirm,
        reservation_models.OrganizationCancel,
        reservation_models.OrganizationTemporarilyRejected,
        reservation_models.OrganizationRefuse,
        reservation_models.RequesterConfirm,
        reservation_models.RequesterCancel,
    ]
    list_filter = [PolymorphicChildModelFilter]
    autocomplete_fields = [*LogInfoAdminMixin.autocomplete_fields]


@admin.register(reservation_models.OrganizationConfirm)
class OrganizationConfirmAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = reservation_models.ReservationUpdate  # Explicitly set here!
    # define custom features here


@admin.register(reservation_models.OrganizationCancel)
class OrganizationCancelAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = reservation_models.ReservationUpdate  # Explicitly set here!
    # define custom features here


@admin.register(reservation_models.OrganizationTemporarilyRejected)
class OrganizationTemporarilyRejectedAdmin(
    PolymorphicChildModelAdmin,
    LogInfoAdminMixin,
):
    base_model = reservation_models.ReservationUpdate  # Explicitly set here!
    # define custom features here


@admin.register(reservation_models.GuestInvite)
class GuestInviteAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = reservation_models.ReservationUpdate  # Explicitly set here!
    # define custom features here


@admin.register(reservation_models.OrganizationRefuse)
class OrganizationRefuseAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = reservation_models.ReservationUpdate  # Explicitly set here!
    # define custom features here


@admin.register(reservation_models.RequesterConfirm)
class RequesterConfirmAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = reservation_models.ReservationUpdate  # Explicitly set here!
    # define custom features here


@admin.register(reservation_models.RequesterCancel)
class RequesterCancelAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = reservation_models.ReservationUpdate  # Explicitly set here!
    # define custom features here


@admin.register(reservation_models.WaitingUserEmailConfirmation)
class WaitingUserEmailConfirmationAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = reservation_models.ReservationUpdate  # Explicitly set here!
    # define custom features here


@admin.register(reservation_models.InvalidReservation)
class InvalidReservationAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = reservation_models.ReservationUpdate  # Explicitly set here!
    # define custom features here


@admin.register(reservation_models.ReservationLine)
class ReservationLineAdmin(admin.ModelAdmin):
    readonly_fields = ["total_price", "minimum_amount", "maximum_amount"]
    list_display = [
        "__str__",
        "reservation",
        "amount",
        "price_matrix_item",
        "total_price",
        "minimum_amount",
        "maximum_amount",
    ]


@admin.register(reservation_models.ReservationSettings)
class ReservationSettingsAdmin(PolymorphicParentModelAdmin):
    base_model = reservation_models.ReservationSettings
    child_models = [
        reservation_models.ReservationSettings,
        reservation_models.EventReservationSettings,
    ]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(reservation_models.EventReservationSettings)
class EventReservationSettingsAdmin(PolymorphicChildModelAdmin):
    base_model = reservation_models.ReservationSettings  # Explicitly set here!
    # define custom features here
