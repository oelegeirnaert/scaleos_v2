from django.contrib import admin

from scaleos.hr import models as hr_models
from scaleos.organizations.admin import OrganizationOwnerInlineAdmin
from scaleos.shared.admin import LogInfoInlineAdminMixin


# Register your models here.
class PersonAddressInlineAdmin(admin.TabularInline):
    model = hr_models.PersonAddress
    extra = 0
    show_change_link = True


class PersonTelephoneNumberInlineAdmin(LogInfoInlineAdminMixin):
    model = hr_models.PersonTelephoneNumber
    extra = 0
    show_change_link = True


class PersonLanguageInlineAdmin(LogInfoInlineAdminMixin):
    model = hr_models.PersonLanguage
    extra = 0
    show_change_link = True


@admin.register(hr_models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "user",
        "name",
        "family_name",
        "primary_email_address",
        "primary_telephone_number",
    ]
    readonly_fields = ["age", "primary_telephone_number"]
    search_fields = ["name", "national_number"]
    inlines = [
        PersonAddressInlineAdmin,
        OrganizationOwnerInlineAdmin,
        PersonTelephoneNumberInlineAdmin,
        PersonLanguageInlineAdmin,
    ]
