from django.contrib import admin
from django.utils.translation import gettext_lazy as _
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
    ]
    list_display = ["price_text"]
    inlines = [PriceHistoryInlineAdmin]