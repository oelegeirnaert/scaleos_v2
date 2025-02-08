from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicParentModelAdmin

from scaleos.payments import models as payment_models

# Register your models here.


class PriceHistoryInlineAdmin(admin.TabularInline):
    model = payment_models.PriceHistory
    extra = 0
    show_change_link = True
    readonly_fields = ["created_on"]


class AgePriceMatrixItemInlineAdmin(admin.TabularInline):
    model = payment_models.AgePriceMatrixItem
    extra = 0
    show_change_link = True


class BulkPriceMatrixItemInlineAdmin(admin.TabularInline):
    model = payment_models.BulkPriceMatrixItem
    extra = 0
    show_change_link = True


@admin.register(payment_models.Price)
class PriceAdmin(admin.ModelAdmin):
    readonly_fields = [
        "created_on",
        "modified_on",
        "price_text",
        "previous_price",
        "price",
        "price_vat_included",
        "price_vat_excluded",
        "public_key",
    ]
    list_display = ["price_text"]
    inlines = [PriceHistoryInlineAdmin]


@admin.register(payment_models.AgePriceMatrix)
class AgePriceMatrixAdmin(PolymorphicChildModelAdmin):
    base_model = payment_models.AgePriceMatrix  # Explicitly set here!
    # define custom features here
    inlines = [AgePriceMatrixItemInlineAdmin]


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


@admin.register(payment_models.AgePriceMatrixItem)
class AgePriceMatrixItemAdmin(admin.ModelAdmin):
    pass


@admin.register(payment_models.BulkPriceMatrixItem)
class BulkPriceMatrixItemAdmin(admin.ModelAdmin):
    pass
