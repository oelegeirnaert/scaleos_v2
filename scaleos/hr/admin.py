from django.contrib import admin

from scaleos.hr import models as hr_models


# Register your models here.
@admin.register(hr_models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "user",
        "primary_email_address",
        "primary_telephone_number",
    ]
    readonly_fields = ["age"]
    search_fields = ["name", "national_number"]
