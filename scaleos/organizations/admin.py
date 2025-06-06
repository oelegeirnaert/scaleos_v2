from django.contrib import admin
from leaflet.admin import LeafletGeoAdminMixin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.organizations import models as organization_models
from scaleos.websites import models as website_models
from scaleos.payments.admin import PaymentMethodInlineAdmin

# Register your models here.


class OrganizationInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class OrganizationInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.Organization
        show_change_link = True

    class EnterpriseInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.Enterprise
        show_change_link = True

    model = organization_models.Organization
    child_inlines = (
        OrganizationInlineAdmin,
        EnterpriseInlineAdmin,
    )


class OrganizationAddressInlineAdmin(admin.TabularInline):
    model = organization_models.OrganizationAddress
    extra = 0
    show_change_link = True


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

    class OrganizationMemberInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.OrganizationMember
        show_change_link = True

    model = organization_models.OrganizationMember
    child_inlines = (
        OrganizationOwnerInlineAdmin,
        OrganizationEmployeeInlineAdmin,
        OrganizationMemberInlineAdmin,
    )

class CustomerInlineAdmin(StackedPolymorphicInline):
    class B2CInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.B2CCustomer
        show_change_link = True


    class B2BInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.B2BCustomer
        show_change_link = True

    class CustomerInlineAdmin(StackedPolymorphicInline.Child):
        model = organization_models.Customer
        show_change_link = True



    model = organization_models.Customer
    child_inlines = (
        CustomerInlineAdmin,
        B2CInlineAdmin,
        B2BInlineAdmin,
    )



class OrganizationStylingInlineAdmin(admin.TabularInline):
    model = organization_models.OrganizationStyling
    extra = 0
    show_change_link = True




@admin.register(organization_models.Organization)
class OrganizationAdmin(
    LeafletGeoAdminMixin,
    PolymorphicInlineSupportMixin,
    PolymorphicParentModelAdmin,
):
    base_model = organization_models.Organization
    child_models = [
        organization_models.Organization,  # Delete once a submodel has been added.
        organization_models.Enterprise,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["name"]
    search_fields = ["number", "name"]
    readonly_fields = ["slug"]
    inlines = [
        OrganizationAddressInlineAdmin,
        OrganizationMemberInlineAdmin,
        OrganizationStylingInlineAdmin,
        PaymentMethodInlineAdmin,
        CustomerInlineAdmin,
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "primary_domain":
            obj_id = request.resolver_match.kwargs.get("object_id")
            if obj_id:
                try:
                    org = organization_models.Organization.objects.get(pk=obj_id)
                    # Get all domains from websites belonging to this org
                    domain_qs = website_models.WebsiteDomain.objects.filter(website__organization=org)
                    kwargs["queryset"] = domain_qs
                except organization_models.Organization.DoesNotExist:
                    kwargs["queryset"] = website_models.WebsiteDomain.objects.none()
            else:
                kwargs["queryset"] = website_models.WebsiteDomain.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(organization_models.Enterprise)
class EnterpriseAdmin(
    OrganizationAdmin,
    PolymorphicChildModelAdmin,
):
    base_model = organization_models.Organization  # Explicitly set here!
    readonly_fields = ["slug", "public_key"]
    # define custom features here


@admin.register(organization_models.OrganizationStyling)
class OrganizationStylingAdmin(admin.ModelAdmin):
    pass




@admin.register(organization_models.OrganizationMember)
class OrganizationMemberAdmin(PolymorphicParentModelAdmin):
    base_model = organization_models.OrganizationMember
    child_models = [
        organization_models.OrganizationMember,
        organization_models.OrganizationOwner,
        organization_models.OrganizationEmployee,
    ]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(organization_models.OrganizationOwner)
class OrganizationOwnerAdmin(PolymorphicChildModelAdmin):
    base_model = organization_models.OrganizationMember


@admin.register(organization_models.OrganizationEmployee)
class OrganizationEmployeeAdmin(PolymorphicChildModelAdmin):
    base_model = organization_models.OrganizationMember

@admin.register(organization_models.Customer)
class CustomerAdmin(PolymorphicParentModelAdmin):
    base_model = organization_models.Customer
    child_models = [
        organization_models.Customer,
        organization_models.B2BCustomer,
        organization_models.B2CCustomer,
    ]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(organization_models.B2CCustomer)
class B2CCustomerAdmin(CustomerAdmin, PolymorphicChildModelAdmin):
    base_model = organization_models.Customer


@admin.register(organization_models.B2BCustomer)
class B2BCustomerAdmin(CustomerAdmin, PolymorphicChildModelAdmin):
    base_model = organization_models.Customer

