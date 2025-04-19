from django.contrib import admin
from leaflet.admin import LeafletGeoAdminMixin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin

from scaleos.organizations import models as organization_models

# Register your models here.


class OrganizationOwnerInlineAdmin(admin.TabularInline):
    model = organization_models.OrganizationOwner
    extra = 0
    show_change_link = True
    autocomplete_fields = ["person"]


class OrganizationStylingInlineAdmin(admin.TabularInline):
    model = organization_models.OrganizationStyling
    extra = 0
    show_change_link = True


class OrganizationPaymentMethodInlineAdmin(admin.TabularInline):
    model = organization_models.OrganizationPaymentMethod
    extra = 0
    show_change_link = True


class OrganizationCustomerInlineAdmin(admin.TabularInline):
    model = organization_models.OrganizationCustomer
    extra = 0
    show_change_link = True
    autocomplete_fields = ["b2c", "b2b"]
    fk_name = "organization"


@admin.register(organization_models.Enterprise)
class EnterpriseAdmin(
    LeafletGeoAdminMixin,
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
):
    base_model = organization_models.Organization  # Explicitly set here!
    readonly_fields = ["slug", "public_key"]
    # define custom features here
    inlines = [
        OrganizationOwnerInlineAdmin,
        OrganizationCustomerInlineAdmin,
        OrganizationStylingInlineAdmin,
        OrganizationPaymentMethodInlineAdmin,
    ]


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


@admin.register(organization_models.OrganizationCustomer)
class OrganizationCustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(organization_models.OrganizationStyling)
class OrganizationStylingAdmin(admin.ModelAdmin):
    pass


@admin.register(organization_models.OrganizationPaymentMethod)
class OrganizationPaymentMethodAdmin(admin.ModelAdmin):
    pass
