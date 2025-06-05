from django.contrib import admin
from leaflet.admin import LeafletGeoAdminMixin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.buildings import models as building_models


# Inlines for ownership and tenancy on building
class BuildingOwnerInline(admin.TabularInline):
    model = building_models.BuildingOwner
    extra = 0
    show_change_link = True


class BuildingTenantInline(admin.TabularInline):
    model = building_models.BuildingTenant
    extra = 0
    show_change_link = True


# Inlines for ownership and tenancy on floors
class FloorOwnerInline(admin.TabularInline):
    model = building_models.FloorOwner
    extra = 0
    show_change_link = True


class BuildingRoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline):
    model = building_models.Room

    class RoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.Room
        show_change_link = True

    class BathRoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.BathRoom
        show_change_link = True

    class HotelRoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.HotelRoom
        show_change_link = True

    class LivingRoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.LivingRoom
        show_change_link = True

    class KitchenInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.Kitchen
        show_change_link = True

    class BedRoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.BedRoom
        show_change_link = True

    class OfficeInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.Office
        show_change_link = True

    class GarageInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.Garage
        show_change_link = True

    class MeetingRoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.MeetingRoom
        show_change_link = True

    class LaundryRoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.LaundryRoom
        show_change_link = True

    class FitnessRoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.FitnessRoom
        show_change_link = True

    class SpaRoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.SpaRoom
        show_change_link = True

    class SaunaRoomInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.SaunaRoom
        show_change_link = True

    class WCInlineAdmin(LeafletGeoAdminMixin, StackedPolymorphicInline.Child):
        model = building_models.WC
        show_change_link = True

    child_inlines = (
        RoomInlineAdmin,
        BathRoomInlineAdmin,
        HotelRoomInlineAdmin,
        LivingRoomInlineAdmin,
        KitchenInlineAdmin,
        BedRoomInlineAdmin,
        OfficeInlineAdmin,
        GarageInlineAdmin,
        MeetingRoomInlineAdmin,
        LaundryRoomInlineAdmin,
        FitnessRoomInlineAdmin,
        SpaRoomInlineAdmin,
        SaunaRoomInlineAdmin,
        WCInlineAdmin,
    )


class FloorTenantInline(admin.TabularInline):
    model = building_models.FloorTenant
    extra = 0
    show_change_link = True


# Inline for FloorLayout on Floor
class FloorLayoutInline(admin.TabularInline):
    model = building_models.FloorLayout
    extra = 0
    show_change_link = True


# Child inlines for Floor polymorphic children


class RoomInline(StackedPolymorphicInline.Child):
    model = building_models.Room
    show_change_link = True


class TerraceInline(StackedPolymorphicInline.Child):
    model = building_models.Terrace
    show_change_link = True


# Parent inline for Floor in Building admin
class FloorInline(StackedPolymorphicInline):
    model = building_models.Floor
    child_inlines = (
        RoomInline,
        TerraceInline,
    )


# Building admin with inlines for owners, tenants and floors
@admin.register(building_models.Building)
class BuildingAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    list_display = ["name"]
    inlines = [
        BuildingOwnerInline,
        BuildingTenantInline,
        BuildingRoomInlineAdmin,
    ]


# Floor parent admin for polymorphic children Room and Terrace
@admin.register(building_models.Floor)
class FloorAdmin(PolymorphicParentModelAdmin):
    base_model = building_models.Floor
    child_models = (
        building_models.Floor,
        building_models.Room,
        building_models.Terrace,
    )
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["id", "name", "level", "square_metres"]


# Polymorphic child admin for Room with ownership, tenancy and layout inlines
@admin.register(building_models.Room)
class RoomAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin):
    base_model = building_models.Floor
    inlines = [
        FloorOwnerInline,
        FloorTenantInline,
        FloorLayoutInline,
    ]


@admin.register(building_models.BedRoom)
class BedRoomAdmin(RoomAdmin):
    base_model = building_models.Floor


@admin.register(building_models.BathRoom)
class BathRoomAdmin(RoomAdmin):
    base_model = building_models.Floor


# Polymorphic child admin for Terrace with ownership, tenancy and layout inlines
@admin.register(building_models.Terrace)
class TerraceAdmin(PolymorphicChildModelAdmin):
    base_model = building_models.Floor
    inlines = [
        FloorOwnerInline,
        FloorTenantInline,
        FloorLayoutInline,
    ]


@admin.register(building_models.Party)
class PartyAdmin(PolymorphicParentModelAdmin):
    base_model = building_models.Party
    child_models = (
        building_models.Party,
        building_models.Person,
        building_models.Organization,
    )
    list_filter = (PolymorphicChildModelFilter,)
    list_display = ("__str__", "polymorphic_ctype")


@admin.register(building_models.Person)
class PersonAdmin(PolymorphicChildModelAdmin):
    base_model = building_models.Person
    show_in_index = True
    list_display = ("linked_person",)


@admin.register(building_models.Organization)
class OrganizationAdmin(PolymorphicChildModelAdmin):
    base_model = building_models.Organization
    show_in_index = True
    list_display = ("linked_organization",)
