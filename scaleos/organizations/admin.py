from django.contrib import admin
from leaflet.admin import LeafletGeoAdminMixin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicParentModelAdmin

from scaleos.organizations import models as organization_models

# Register your models here.


class OrganizationOwnerInlineAdmin(admin.TabularInline):
    model = organization_models.OrganizationOwner
    extra = 0
    show_change_link = True


@admin.register(organization_models.Enterprise)
class EnterpriseAdmin(LeafletGeoAdminMixin, PolymorphicChildModelAdmin):
    base_model = organization_models.Organization  # Explicitly set here!
    readonly_fields = ["slug", "public_key"]
    # define custom features here


@admin.register(organization_models.Organization)
class OrganizationAdmin(LeafletGeoAdminMixin, PolymorphicParentModelAdmin):
    base_model = organization_models.Organization
    child_models = [
        organization_models.Organization,  # Delete once a submodel has been added.
        organization_models.Enterprise,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["name"]
    search_fields = ["number", "name"]
    readonly_fields = ["slug"]
