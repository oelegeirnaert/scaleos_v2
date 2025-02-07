from django.db import models
from polymorphic.models import PolymorphicModel
from scaleos.shared.mixins import AdminLinkMixin, ITS_NOW
from scaleos.shared.fields import NameField
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Concept(PolymorphicModel, NameField):
    organizer = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        null=True,
    )
    class Meta:
        verbose_name = _("concept")
        verbose_name_plural = _("concepts")   

class WeddingConcept(Concept):
    def generate_events(self):
        ceremony, ceremony_created = Ceremony.objects.get_or_create(concept_id=self.id)
        ceremony.name = f"Ceremony {self.name}"
        ceremony.save()

        reception, reception_created = Reception.objects.get_or_create(
            concept_id=self.id,
        )
        reception.name = f"Reception {self.name}"
        reception.save()

        dinner, dinner_created = Dinner.objects.get_or_create(concept_id=self.id)
        dinner.name = f"Dinner {self.name}"
        dinner.save()

        dance, dance_created = Dance.objects.get_or_create(concept_id=self.id)
        dance.name = f"Dansfeest {self.name}"
        dance.save()

        closing, closing_created = Closing.objects.get_or_create(concept_id=self.id)
        closing.name = f"Afsluit {self.name}"
        closing.save()

        Concept.objects.filter(id=self.id).update(force_event_generation=False)

class BrunchConcept(Concept):
    pass

class DinnerAndDanceConcept(Concept):
    def generate_events(self):
        dinner, dinner_created = Dinner.objects.get_or_create(concept_id=self.id)
        dinner.name = f"Dinner {self.name}"
        dinner.save()

        dance, dance_created = Dance.objects.get_or_create(concept_id=self.id)
        dance.name = f"Dance {self.name}"
        dance.save()

        Concept.objects.filter(id=self.id).update(force_event_generation=False)

class Event(PolymorphicModel, NameField):
    concept = models.ForeignKey(
        Concept,
        related_name="events",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    expected_number_of_guests = models.IntegerField(null=True, blank=True)
    minimum_number_of_guests = models.IntegerField(null=True, blank=True)
    maximum_number_of_guests = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")

class SingleEvent(Event):
    class STATUS(models.TextChoices):
        UPCOMING = 'UPCOMING', _('upcoming')
        ONGOING = 'ONGOING', _('ongoing')
        ENDED = "ENDED", _("ended")
        UNKNOWN = "UNKNOWN", _("unknown")

    show_in_ongoing_events = models.BooleanField(default=True)
    starting_at = models.DateTimeField(null=True)
    ending_on = models.DateTimeField(null=True)
    """ 
    location = models.ForeignKey(
        "geography.Location",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    catering = models.ForeignKey(
        "caterers.Catering",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    ) 
    """

    @property
    def status(self):
        if self.starting_at and ITS_NOW < self.starting_at:
            return SingleEvent.STATUS.UPCOMING
        if (
            self.starting_at
            and self.ending_on
            and self.starting_at < ITS_NOW < self.ending_on
        ):
            return SingleEvent.STATUS.ONGOING

        if self.ending_on and ITS_NOW > self.ending_on:
            return SingleEvent.STATUS.ENDED

        return SingleEvent.STATUS.UNKNOWN

    @property
    def status_text(self):
        if self.status == SingleEvent.STATUS.UPCOMING:
            return _(f"upcoming, on {self.starting_at}")
        
        if self.status == SingleEvent.STATUS.ONGOING:
            return _(f"ongoing... ending on {self.ending_on}")

        if self.status == SingleEvent.STATUS.ENDED:
            return f"{self.verbose_name} is over"

        return "unknown status...."
    
class Dance(SingleEvent):
    pass

class Dinner(SingleEvent):
    ICON = "local_dining"
    

class Brunch(SingleEvent):
    ICON = "local_dining"
    

class Ceremony(SingleEvent):
    ICON = "visibility"

class Reception(SingleEvent):
    ICON = "wc"
    
class Closing(SingleEvent):
    ICON = "hotel"


class Break(SingleEvent):
    ICON = "pause"
    