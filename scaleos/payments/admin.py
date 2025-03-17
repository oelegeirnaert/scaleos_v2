from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.payments import models as payment_models
from scaleos.shared import admin as shared_admin

# Register your models here.


class PaymentInlineAdmin(
    StackedPolymorphicInline,
    shared_admin.LogInfoInlineAdminMixin,
):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class PaymentInlineAdmin(
        StackedPolymorphicInline.Child,
        shared_admin.LogInfoInlineAdminMixin,
    ):
        model = payment_models.Payment
        show_change_link = True

    class EPCMoneyTransferPaymentInlineAdmin(
        StackedPolymorphicInline.Child,
        shared_admin.LogInfoInlineAdminMixin,
    ):
        model = payment_models.EPCMoneyTransferPayment
        show_change_link = True

    model = payment_models.Payment
    child_inlines = (
        PaymentInlineAdmin,
        EPCMoneyTransferPaymentInlineAdmin,
    )


class PriceHistoryInlineAdmin(shared_admin.LogInfoInlineAdminMixin):
    model = payment_models.PriceHistory
    extra = 0
    show_change_link = True
    readonly_fields = [
        "vat_included",
        "vat_excluded",
        "vat",
        "modified_on",
        *shared_admin.LogInfoInlineAdminMixin.readonly_fields,
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
class PriceAdmin(shared_admin.LogInfoAdminMixin):
    readonly_fields = [
        "text",
        "previous_price",
        "vat_included",
        "vat_excluded",
        "public_key",
        *shared_admin.LogInfoAdminMixin.readonly_fields,
    ]
    list_display = ["text"]
    inlines = [PriceHistoryInlineAdmin]


@admin.register(payment_models.AgePriceMatrix)
class AgePriceMatrixAdmin(PolymorphicChildModelAdmin):
    base_model = payment_models.AgePriceMatrix  # Explicitly set here!
    # define custom features here
    inlines = [AgePriceMatrixItemInlineAdmin]
    readonly_fields = ["public_key"]


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
class PaymentAdmin(PolymorphicParentModelAdmin, shared_admin.LogInfoAdminMixin):
    base_model = payment_models.Payment
    child_models = [
        payment_models.Payment,  # Delete once a submodel has been added.
        payment_models.EPCMoneyTransferPayment,
    ]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(payment_models.EPCMoneyTransferPayment)
class EPCMoneyTransferPaymentAdmin(
    PolymorphicChildModelAdmin,
    shared_admin.LogInfoAdminMixin,
):
    base_model = payment_models.EPCMoneyTransferPayment  # Explicitly set here!
    # define custom features here


@admin.register(payment_models.PaymentRequest)
class PaymentRequestAdmin(
    PolymorphicInlineSupportMixin,
    shared_admin.LogInfoAdminMixin,
):
    inlines = [PaymentInlineAdmin]
    readonly_fields = [
        "already_paid",
        "still_to_pay",
        "fully_paid",
        *shared_admin.LogInfoAdminMixin.readonly_fields,
    ]


@admin.register(payment_models.PriceMatrixItem)
class PriceMatrixItemAdmin(admin.ModelAdmin):
    pass
