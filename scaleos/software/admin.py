from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicParentModelAdmin

from scaleos.software import models as software_models

# Register your models here.


class ServiceInlineAdmin(admin.TabularInline):
    model = software_models.Service
    extra = 0
    show_change_link = True


@admin.register(software_models.Service)
class ServiceAdmin(PolymorphicParentModelAdmin):
    base_model = software_models.Service
    child_models = [
        software_models.Service,  # Delete once a submodel has been added.
        software_models.OllamaService,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(software_models.OllamaService)
class OllamaServiceAdmin(PolymorphicChildModelAdmin):
    base_model = software_models.Service  # Explicitly set here!
    # define custom features here)
