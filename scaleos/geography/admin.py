from django.contrib import admin
from leaflet.admin import LeafletGeoAdminMixin

from scaleos.geography import models as geography_models

# Register your models here.


@admin.register(geography_models.Address)
class AddressAdmin(LeafletGeoAdminMixin, admin.ModelAdmin):
    readonly_fields = ["gps_address"]
