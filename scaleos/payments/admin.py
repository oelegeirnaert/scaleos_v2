from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.safestring import mark_safe
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
from scaleos.shared.admin import OriginStackedAdminMixin
from scaleos.shared.admin import generic_relation_reverse_link

# Register your models here.


def price_link(self, obj):
    """Displays a link to edit the Price or an ADD button if missing."""
    if obj.id is None:
        return _("add your price after saving...")

    price = obj.price.first()  # Using GenericRelation

    if price:
        url = reverse(
            "admin:payments_price_change",
            args=[price.id],
        )  # Adjust "app_price" based on your app name
        return mark_safe(f'<a href="{url}">Edit {price}</a>')  # noqa: S308
    unique_content_type_id = ContentType.objects.get_for_model(obj).id
    add_url = reverse(
        "admin:payments_price_add",
    )  # Adjust "app_price" based on your app name
    return mark_safe(  # noqa: S308
        f'<a href="{add_url}?unique_origin_content_type={unique_content_type_id}&unique_origin_object_id={obj.id}" class="button">➕ Add Price</a>',  # noqa: E501, RUF001
    )


class VATPriceLineInlineAdmin(admin.TabularInline):
    model = payment_models.VATPriceLine
    extra = 0
    show_change_link = True
    readonly_fields = ["vat_included", "vat_excluded", "vat"]


class EventReservationPaymentConditionInlineAdmin(LogInfoStackedInlineAdminMixin):
    model = payment_models.EventReservationPaymentCondition
    extra = 0
    show_change_link = True

    @admin.display(
        description="Price",
    )
    def price_link(self, obj):
        return price_link(self, obj)

    readonly_fields = ["price_link"]


class PriceLinkTabularStackedAdminMixin(admin.StackedInline):
    @admin.display(
        description="Price",
    )
    def price_link(self, obj):
        return price_link(self, obj)

    readonly_fields = ["price_link"]


class PriceLinkTabularInlineAdminMixin(admin.TabularInline):
    @admin.display(
        description="Price",
    )
    def price_link(self, obj):
        return price_link(self, obj)

    readonly_fields = ["price_link"]


class PriceLinkAdminMixin(admin.ModelAdmin):
    @admin.display(
        description="Price",
    )
    def price_link(self, obj):
        return price_link(self, obj)

    readonly_fields = ["price_link"]


class PaymentProposalInlineAdmin(
    LogInfoStackedInlineAdminMixin,
    PriceLinkTabularStackedAdminMixin,
):
    model = payment_models.PaymentProposal
    extra = 0
    show_change_link = True
    readonly_fields = ["origin_link", *LogInfoStackedInlineAdminMixin.readonly_fields]

    @admin.display(
        description=_("origin link"),
    )
    def origin_link(self, obj):
        return generic_relation_reverse_link(self, obj, "origin")


class PaymentInlineAdmin(
    StackedPolymorphicInline,
    LogInfoInlineAdminMixin,
    OriginStackedAdminMixin,
):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class PaymentInlineAdmin(
        StackedPolymorphicInline.Child,
        LogInfoInlineAdminMixin,
        OriginStackedAdminMixin,
    ):
        model = payment_models.Payment
        show_change_link = True

    class EPCMoneyTransferPaymentInlineAdmin(
        StackedPolymorphicInline.Child,
        LogInfoInlineAdminMixin,
        OriginStackedAdminMixin,
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
        "unique_origin_link",
        "previous_price",
        "vat_included",
        "vat_excluded",
        "vat",
        "public_key",
        *LogInfoAdminMixin.readonly_fields,
    ]
    list_display = ["id", "__str__", "unique_origin_link"]
    inlines = [VATPriceLineInlineAdmin, PriceHistoryInlineAdmin]
    list_filter = ["organization"]

    @admin.display(
        description=_("unique origin link"),
    )
    def unique_origin_link(self, obj):
        return generic_relation_reverse_link(self, obj, "unique_origin")


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
class AgePriceMatrixItemAdmin(PriceLinkAdminMixin):
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
    PriceLinkAdminMixin,
):
    inlines = [PaymentProposalInlineAdmin, PaymentInlineAdmin]
    readonly_fields = [
        "to_pay",
        # "already_paid",
        # "still_to_pay",
        # "fully_paid",
        "payment_methods",
        "origin_link",
        *LogInfoAdminMixin.readonly_fields,
        *PriceLinkAdminMixin.readonly_fields,
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

    @admin.display(
        description=_("origin link"),
    )
    def origin_link(self, obj):
        return generic_relation_reverse_link(self, obj, "origin")


@admin.register(payment_models.PriceMatrixItem)
class PriceMatrixItemAdmin(admin.ModelAdmin):
    readonly_fields = ["current_price", "price_link"]

    @admin.display(
        description=_("price link"),
    )
    def price_link(self, obj):
        return generic_relation_reverse_link(self, obj, "price")


@admin.register(payment_models.PaymentSettings)
class PaymentSettingsAdmin(PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin):
    base_model = payment_models.PaymentSettings
    child_models = [
        payment_models.PaymentSettings,
        payment_models.EventReservationPaymentSettings,
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
class PaymentProposalAdmin(PriceLinkAdminMixin):
    pass


@admin.register(payment_models.EventReservationPaymentSettings)
class EventReservationPaymentSettingsAdmin(
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
    LogInfoAdminMixin,
):
    base_model = payment_models.PaymentSettings
    inlines = [EventReservationPaymentConditionInlineAdmin]


@admin.register(payment_models.EventReservationPaymentCondition)
class EventReservationPaymentConditionAdmin(LogInfoAdminMixin):
    pass


@admin.register(payment_models.VATPriceLine)
class VATPriceLineAdmin(admin.ModelAdmin):
    readonly_fields = ["vat_included", "vat_excluded", "vat"]
