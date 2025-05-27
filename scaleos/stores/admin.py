from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin

from scaleos.stores import models as store_models


# Register your models here.
@admin.register(store_models.Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "organization")
    search_fields = ("name",)


@admin.register(store_models.PurchasableItem)
class PurchasableItemdmin(PolymorphicParentModelAdmin):
    base_model = store_models.PurchasableItem
    child_models = [
        store_models.PurchasableItem,
        store_models.Product,
        store_models.Service,
    ]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(store_models.Product)
class ProductAdmin(
    PurchasableItemdmin,
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
):
    base_model = store_models.PurchasableItem  # Explicitly set here!
    # define custom features here


@admin.register(store_models.Service)
class ServiceAdmin(
    PurchasableItemdmin,
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
):
    base_model = store_models.PurchasableItem  # Explicitly set here!
    # define custom features here
