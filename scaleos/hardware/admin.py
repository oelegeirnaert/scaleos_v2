from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicParentModelAdmin

from scaleos.hardware import models as hardware_models
from scaleos.software.admin import ServiceInlineAdmin

# Register your models here.


class ComputerInlineAdmin(admin.TabularInline):
    model = hardware_models.Computer
    extra = 0
    show_change_link = True


@admin.register(hardware_models.Device)
class DeviceAdmin(PolymorphicParentModelAdmin, admin.ModelAdmin):
    base_model = hardware_models.Device
    child_models = [
        hardware_models.Device,  # Delete once a submodel has been added.
        hardware_models.Computer,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(hardware_models.Computer)
class ComputerAdmin(PolymorphicChildModelAdmin, admin.ModelAdmin):
    base_model = hardware_models.Device  # Explicitly set here!
    inlines = [ServiceInlineAdmin]
    # define custom features here)


@admin.register(hardware_models.Network)
class NetworkAdmin(admin.ModelAdmin):
    inlines = [ComputerInlineAdmin]
