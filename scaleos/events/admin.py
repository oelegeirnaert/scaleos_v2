from django.contrib import admin
from scaleos.events import models as event_models
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import PolymorphicChildModelAdmin

# Register your models here.

@admin.register(event_models.WeddingConcept)
class WeddingConceptAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.WeddingConcept  # Explicitly set here!
    # define custom features here

@admin.register(event_models.BrunchConcept)
class BrunchConceptAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.BrunchConcept  # Explicitly set here!
    # define custom features here

@admin.register(event_models.DinnerAndDanceConcept)
class DinnerAndDanceConceptAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.DinnerAndDanceConcept  # Explicitly set here!
    # define custom features here

@admin.register(event_models.Concept)
class ConceptAdmin(PolymorphicParentModelAdmin):
    base_model = event_models.Concept
    child_models = [
        event_models.Concept,  # Delete once a submodel has been added.
        event_models.WeddingConcept,
        event_models.BrunchConcept,
        event_models.DinnerAndDanceConcept,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["name"]
    search_fields = ["name"]

@admin.register(event_models.Brunch)
class BrunchAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.SingleEvent  # Explicitly set here!
    # define custom features here

@admin.register(event_models.SingleEvent)
class SingleEventAdmin(PolymorphicChildModelAdmin):
    base_model = event_models.Event  # Explicitly set here!
    # define custom features here

@admin.register(event_models.Event)
class OrganizationAdmin(PolymorphicParentModelAdmin):
    base_model = event_models.Event
    child_models = [
        event_models.Event,  # Delete once a submodel has been added.
        event_models.SingleEvent,
    ]
    list_filter = [PolymorphicChildModelFilter]
    list_display = ["name"]
    search_fields = ["name"]
