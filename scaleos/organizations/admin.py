from django.contrib import admin
from leaflet.admin import LeafletGeoAdminMixin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.organizations import models as organization_models

# Register your models here.


class OrganizationMemberInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class OrganizationOwnerInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.OrganizationOwner
        show_change_link = True

    class OrganizationEmployeeInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.OrganizationEmployee
        show_change_link = True

    class OrganizationCustomerInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.OrganizationCustomer
        show_change_link = True

    class OrganizationMemberInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.OrganizationMember
        show_change_link = True

    class B2BCustomerInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.B2BCustomer
        show_change_link = True

    model = organization_models.OrganizationMember
    child_inlines = (
        OrganizationOwnerInlineAdmin,
        OrganizationEmployeeInlineAdmin,
        OrganizationCustomerInlineAdmin,
        OrganizationMemberInlineAdmin,
        B2BCustomerInlineAdmin,
    )


class OrganizationStylingInlineAdmin(admin.TabularInline):
    model = organization_models.OrganizationStyling
    extra = 0
    show_change_link = True


class OrganizationPaymentMethodInlineAdmin(admin.TabularInline):
    model = organization_models.OrganizationPaymentMethod
    extra = 0
    show_change_link = True


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
        # OrganizationOwnerInlineAdmin,
        # OrganizationCustomerInlineAdmin,
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


@admin.register(organization_models.OrganizationStyling)
class OrganizationStylingAdmin(admin.ModelAdmin):
    pass


@admin.register(organization_models.OrganizationPaymentMethod)
class OrganizationPaymentMethodAdmin(admin.ModelAdmin):
    pass


@admin.register(organization_models.OrganizationMember)
class OrganizationMemberAdmin(PolymorphicParentModelAdmin):
    base_model = organization_models.OrganizationMember
    child_models = [
        organization_models.OrganizationMember,
        organization_models.OrganizationOwner,
        organization_models.OrganizationEmployee,
        organization_models.OrganizationCustomer,
        organization_models.B2BCustomer,
    ]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(organization_models.OrganizationOwner)
class OrganizationOwnerAdmin(PolymorphicChildModelAdmin):
    base_model = organization_models.OrganizationMember


@admin.register(organization_models.OrganizationEmployee)
class OrganizationEmployeeAdmin(PolymorphicChildModelAdmin):
    base_model = organization_models.OrganizationMember


@admin.register(organization_models.OrganizationCustomer)
class OrganizationCustomerAdmin(PolymorphicChildModelAdmin):
    base_model = organization_models.OrganizationMember


@admin.register(organization_models.B2BCustomer)
class B2BCustomerAdmin(PolymorphicChildModelAdmin):
    base_model = organization_models.OrganizationCustomer
