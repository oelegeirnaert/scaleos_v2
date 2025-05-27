from django.contrib import admin
from leaflet.admin import LeafletGeoAdminMixin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.buildings import models as building_models

# Register your models here.


# Register your models here.
class BuildingRoomInlineAdmin(
    LeafletGeoAdminMixin,
    PolymorphicInlineSupportMixin,
    admin.StackedInline,
):
    model = building_models.Room
    fk_name = "in_building"
    fields = ["name"]
    show_change_link = True
    extra = 0


class BuildingInlineAdmin(StackedPolymorphicInline):
    model = building_models.Building


@admin.register(building_models.Room)
class RoomAdmin(LeafletGeoAdminMixin, PolymorphicChildModelAdmin):
    base_model = building_models.Floor


@admin.register(building_models.Floor)
class FloorAdmin(
    LeafletGeoAdminMixin,
    PolymorphicInlineSupportMixin,
    PolymorphicParentModelAdmin,
):
    base_model = building_models.Floor
    child_models = [
        building_models.Floor,  # Delete once a submodel has been added.
        building_models.Room,
        building_models.Building,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["name"]
    search_fields = ["name"]
    readonly_fields = ["public_key"]


@admin.register(building_models.Building)
class BuildingAdmin(
    LeafletGeoAdminMixin,
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
):
    base_model = building_models.Floor
    readonly_fields = ["public_key"]
    inlines = [BuildingRoomInlineAdmin]
