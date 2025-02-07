from django.db import models
from polymorphic.models import PolymorphicModel
from scaleos.shared.mixins import AdminLinkMixin, ITS_NOW
from scaleos.shared.fields import NameField
from django.utils.translation import gettext_lazy as _
import datetime

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

    class Meta:
        verbose_name = _("wedding concept")
        verbose_name_plural = _("wedding concepts")

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
    default_starting_time = models.TimeField(null=True, blank=True)
    default_ending_time = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("brunch concept")
        verbose_name_plural = _("brunch concepts")

class DinnerAndDanceConcept(Concept):
    class Meta:
        verbose_name = _("dinner & dance concept")
        verbose_name_plural = _("dinner & dance concepts")

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

    class Meta:
        verbose_name = _("single event")
        verbose_name_plural = _("single events")

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
    
    def set_upcoming_sunday(self):
        today = datetime.date.today()
        next_sunday = today + datetime.timedelta( (6-today.weekday()) % 7 )
        starting_time = datetime.time(12, 0)
        if self.concept and hasattr(self.concept, "default_starting_time"):
            if self.concept.default_starting_time is not None:
                starting_time = self.concept.default_starting_time

        ending_time = datetime.time(23, 0)
        if self.concept and hasattr(self.concept, "default_ending_time"):
            if self.concept.default_ending_time is not None:
                ending_time = self.concept.default_ending_time

        self.starting_at = datetime.datetime.combine(next_sunday, starting_time)
        self.ending_on = datetime.datetime.combine(next_sunday, ending_time)
        self.save()
    
class DanceEvent(SingleEvent):
    class Meta:
        verbose_name = _("dance event")
        verbose_name_plural = _("dance events")

class DinnerEvent(SingleEvent):
    ICON = "local_dining"

    class Meta:
        verbose_name = _("dinner event")
        verbose_name_plural = _("dinner events")
    

class BrunchEvent(SingleEvent):
    ICON = "local_dining"

    class Meta:
        verbose_name = _("brunch event")
        verbose_name_plural = _("brunch events")
    

class CeremonyEvent(SingleEvent):
    ICON = "visibility"

    class Meta:
        verbose_name = _("ceremony event")
        verbose_name_plural = _("ceremony events")

class ReceptionEvent(SingleEvent):
    ICON = "wc"

    class Meta:
        verbose_name = _("reception event")
        verbose_name_plural = _("reception events")
    
class ClosingEvent(SingleEvent):
    ICON = "hotel"

    class Meta:
        verbose_name = _("closing event")
        verbose_name_plural = _("closing events")


class BreakEvent(SingleEvent):
    ICON = "pause"

    class Meta:
        verbose_name = _("break event")
        verbose_name_plural = _("break events")
    