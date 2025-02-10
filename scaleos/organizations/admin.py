from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicParentModelAdmin

from scaleos.organizations import models as organization_models

# Register your models here.


@admin.register(organization_models.Enterprise)
class EnterpriseAdmin(PolymorphicChildModelAdmin):
    base_model = organization_models.Organization  # Explicitly set here!
    readonly_fields = ["slug"]
    # define custom features here


@admin.register(organization_models.Organization)
class OrganizationAdmin(PolymorphicParentModelAdmin):
    base_model = organization_models.Organization
    child_models = [
        organization_models.Organization,  # Delete once a submodel has been added.
        organization_models.Enterprise,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["name"]
    search_fields = ["number", "name"]
    readonly_fields = ["slug"]
