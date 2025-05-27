from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.payments import models as payment_models
from scaleos.shared.admin import LogInfoAdminMixin
from scaleos.shared.admin import LogInfoInlineAdminMixin
from scaleos.shared.admin import LogInfoStackedInlineAdminMixin
from scaleos.shared.admin import build_generic_relation_link

# Register your models here.


class VATPriceLineInlineAdmin(admin.TabularInline):
    model = payment_models.VATPriceLine
    extra = 0
    show_change_link = True
    readonly_fields = ["vat_included", "vat_excluded", "vat"]


class PaymentProposalInlineAdmin(
    LogInfoStackedInlineAdminMixin,
):
    model = payment_models.PaymentProposal
    extra = 0
    show_change_link = True


class PaymentInlineAdmin(
    StackedPolymorphicInline,
    LogInfoInlineAdminMixin,
):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class PaymentInlineAdmin(
        StackedPolymorphicInline.Child,
        LogInfoInlineAdminMixin,
    ):
        model = payment_models.Payment
        show_change_link = True

    class EPCMoneyTransferPaymentInlineAdmin(
        StackedPolymorphicInline.Child,
        LogInfoInlineAdminMixin,
    ):
        model = payment_models.EPCMoneyTransferPayment
        show_change_link = True

    model = payment_models.Payment
    child_inlines = (
        PaymentInlineAdmin,
        EPCMoneyTransferPaymentInlineAdmin,
    )


class PriceHistoryInlineAdmin(LogInfoInlineAdminMixin):
    model = payment_models.PriceHistory
    extra = 0
    show_change_link = True
    readonly_fields = [
        "vat_included",
        "vat_excluded",
        "vat",
        "modified_on",
        *LogInfoInlineAdminMixin.readonly_fields,
    ]

    def has_change_permission(self, request, obj=None):
        return False


class AgePriceMatrixItemInlineAdmin(admin.TabularInline):
    model = payment_models.AgePriceMatrixItem
    extra = 0
    show_change_link = True


class BulkPriceMatrixItemInlineAdmin(admin.TabularInline):
    model = payment_models.BulkPriceMatrixItem
    extra = 0
    show_change_link = True


@admin.register(payment_models.Price)
class PriceAdmin(LogInfoAdminMixin):
    readonly_fields = [
        "previous_price",
        "vat_included",
        "vat_excluded",
        "vat",
        "public_key",
        *LogInfoAdminMixin.readonly_fields,
    ]
    list_display = ["id", "__str__"]
    inlines = [VATPriceLineInlineAdmin, PriceHistoryInlineAdmin]
    list_filter = ["organization"]


@admin.register(payment_models.AgePriceMatrix)
class AgePriceMatrixAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = payment_models.AgePriceMatrix  # Explicitly set here!
    # define custom features here
    inlines = [AgePriceMatrixItemInlineAdmin]
    readonly_fields = ["public_key", *LogInfoAdminMixin.readonly_fields]


@admin.register(payment_models.BulkPriceMatrix)
class BulkPriceMatrixAdmin(PolymorphicChildModelAdmin):
    base_model = payment_models.BulkPriceMatrix  # Explicitly set here!
    # define custom features here
    inlines = [BulkPriceMatrixItemInlineAdmin]


@admin.register(payment_models.PriceMatrix)
class PriceMatrixAdmin(PolymorphicParentModelAdmin):
    base_model = payment_models.PriceMatrix
    child_models = [
        payment_models.PriceMatrix,  # Delete once a submodel has been added.
        payment_models.AgePriceMatrix,
        payment_models.BulkPriceMatrix,
    ]
    list_filter = [PolymorphicChildModelFilter]
    readonly_fields = ["public_key"]


@admin.register(payment_models.AgePriceMatrixItem)
class AgePriceMatrixItemAdmin(admin.ModelAdmin):
    pass


@admin.register(payment_models.BulkPriceMatrixItem)
class BulkPriceMatrixItemAdmin(admin.ModelAdmin):
    pass


@admin.register(payment_models.Payment)
class PaymentAdmin(PolymorphicParentModelAdmin, LogInfoAdminMixin):
    base_model = payment_models.Payment
    child_models = [
        payment_models.Payment,  # Delete once a submodel has been added.
        payment_models.EPCMoneyTransferPayment,
    ]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(payment_models.EPCMoneyTransferPayment)
class EPCMoneyTransferPaymentAdmin(
    PolymorphicChildModelAdmin,
    LogInfoAdminMixin,
):
    base_model = payment_models.EPCMoneyTransferPayment  # Explicitly set here!
    # define custom features here


@admin.register(payment_models.PaymentRequest)
class PaymentRequestAdmin(
    PolymorphicInlineSupportMixin,
    LogInfoAdminMixin,
):
    inlines = [PaymentProposalInlineAdmin, PaymentInlineAdmin]
    readonly_fields = [
        "to_pay",
        "already_paid",
        "still_to_pay",
        "fully_paid",
        "payment_methods",
        "structured_reference_be",
        "structured_reference_sepa",
        *LogInfoAdminMixin.readonly_fields,
    ]
    list_display = [
        "id",
        "to_organization",
        "to_person",
        "already_paid",
        "still_to_pay",
        "fully_paid",
        "origin_object_id",
    ]
    list_filter = ["to_organization", "to_person"]


@admin.register(payment_models.PriceMatrixItem)
class PriceMatrixItemAdmin(admin.ModelAdmin):
    readonly_fields = ["price"]

    @admin.display(description=_("price"))
    def price(self, obj):
        # Use the helper function with the correct attribute name ('notification')
        return build_generic_relation_link(
            obj,
            field_name="price",
            related_model=payment_models.Price,
        )


@admin.register(payment_models.PaymentSettings)
class PaymentSettingsAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin):
    base_model = payment_models.PaymentSettings
    child_models = [
        payment_models.PaymentSettings,
        payment_models.EventReservationPaymentSettings,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["id", "__str__"]


@admin.register(payment_models.PaymentCondition)
class PaymentConditionAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin):
    base_model = payment_models.PaymentCondition
    child_models = [
        payment_models.PaymentCondition,
        payment_models.EventReservationPaymentCondition,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["id", "__str__"]


@admin.register(payment_models.PaymentMethod)
class PaymentMethodAdmin(PolymorphicParentModelAdmin):
    base_model = payment_models.PaymentMethod
    child_models = [
        payment_models.PaymentMethod,
        payment_models.CashPaymentMethod,
        payment_models.EPCMoneyTransferPaymentMethod,
        payment_models.VoucherPaymentMethod,
    ]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(payment_models.EPCMoneyTransferPaymentMethod)
class EPCMoneyTransferPaymentMethodAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = payment_models.PaymentMethod  # Explicitly set here!
    # define custom features here


@admin.register(payment_models.CashPaymentMethod)
class CashPaymentMethodAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = payment_models.PaymentMethod  # Explicitly set here!
    # define custom features here


@admin.register(payment_models.VoucherPaymentMethod)
class VoucherPaymentMethodAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = payment_models.PaymentMethod  # Explicitly set here!
    # define custom features here


@admin.register(payment_models.PaymentProposal)
class PaymentProposalAdmin(admin.ModelAdmin):
    pass


@admin.register(payment_models.EventReservationPaymentSettings)
class EventReservationPaymentSettingsAdmin(
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
    LogInfoAdminMixin,
):
    base_model = payment_models.PaymentSettings


@admin.register(payment_models.EventReservationPaymentCondition)
class EventReservationPaymentConditionAdmin(
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
    LogInfoAdminMixin,
):
    base_model = payment_models.PaymentCondition


@admin.register(payment_models.VATPriceLine)
class VATPriceLineAdmin(admin.ModelAdmin):
    readonly_fields = ["vat_included", "vat_excluded", "vat"]
