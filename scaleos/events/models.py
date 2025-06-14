import datetime
import logging
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from scaleos.catering.models import CateringField
from scaleos.organizations.models import B2BCustomer
from scaleos.organizations.models import Customer
from scaleos.reservations.models import EventReservationSettings
from scaleos.reservations.models import Reservation
from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.fields import SegmentField
from scaleos.shared.mixins import ITS_NOW
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.models import CardModel
from scaleos.timetables.models import TimeTable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Create your models here.

MAX_PERCENTAGE = 100


class Concept(
    PolymorphicModel,
    NameField,
    AdminLinkMixin,
    CardModel,
    PublicKeyField,
    SegmentField,
    CateringField,
):
    organizer = models.ForeignKey(
        "organizations.Organization",
        verbose_name=_(
            "organizer",
        ),
        related_name="concepts",
        on_delete=models.CASCADE,
        null=True,
    )

    slogan = models.CharField(
        verbose_name=_(
            "slogan",
        ),
        default="",
        blank=True,
        max_length=255,
    )

    reservation_settings = models.ForeignKey(
        "reservations.EventReservationSettings",
        verbose_name=_(
            "reservation settings",
        ),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    event_reservation_payment_settings = models.ForeignKey(
        "payments.EventReservationPaymentSettings",
        verbose_name=_(
            "event reservation payment settings",
        ),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    timetable = GenericRelation(
        TimeTable,
        verbose_name=_(
            "timetable",
        ),
        content_type_field="content_type",
        object_id_field="object_id",
    )

    class Meta:
        verbose_name = _("concept")
        verbose_name_plural = _("concepts")

    @property
    def current_price_matrix(self):
        logger.debug("Trying to get the current price matrix for concept %s", self.id)
        if self.price_matrixes.count() == 0:
            logger.info("We cannot find a current price matrix for concept %s", self.id)
            return None

        logger.debug("Checking for date-based price matrixes...")
        results = self.price_matrixes.filter(
            valid_from__lte=ITS_NOW,
            valid_till__gte=ITS_NOW,
        )
        count_results = results.count()
        if count_results == 1:
            logger.debug("One price matrix found on valid from and till")
            return results.first().price_matrix

        results = self.price_matrixes.filter(valid_from__lte=ITS_NOW)
        count_results = results.count()
        if count_results == 1:
            logger.debug("One price matrix found ONLY on valid from property")
            return results.first().price_matrix

        results = self.price_matrixes.filter()
        count_results = results.count()
        if count_results == 1:
            logger.debug("One price matrix found without any date based properties")
            return results.first().price_matrix

        msg = (
            "We don't know which price matrix is currently valid for concept id %s",
            self.id,
        )
        logger.warning(msg)
        return None

    @property
    def upcoming_events(self):
        return self.events.filter(
            singleevent__ending_on__gte=ITS_NOW,
            allow_reservations=True,
            singleevent__parent__isnull=True,
        )

    @property
    def upcoming_events_open_for_reservation(self):
        return [e for e in self.upcoming_events if e.is_open_for_reservations]

    @property
    def starting_at(self):
        return self.events.order_by("-singleevent__starting_at").first().starting_at

    @property
    def ending_on(self):
        return self.events.order_by("-singleevent__ending_on").first().ending_on


class ConceptImage(LogInfoFields):
    concept = models.ForeignKey(
        Concept,
        verbose_name=_(
            "concept",
        ),
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
    )
    image = models.ForeignKey(
        "files.ImageFile",
        verbose_name=_(
            "image",
        ),
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
    )


class CustomerConcept(Concept, LogInfoFields):
    customer = models.ForeignKey(
        "organizations.Customer",
        verbose_name=_(
            "customer",
        ),
        on_delete=models.CASCADE,
        related_name="concepts",
        null=True,
    )

    based_on_concept = models.ForeignKey(
        Concept,
        verbose_name=_(
            "based on concept",
        ),
        on_delete=models.CASCADE,
        related_name="customers",
        null=True,
        blank=True,
    )

    google_fotos_album = models.URLField(
        verbose_name=_(
            "google fotos album",
        ),
        default="",
        blank=True,
    )

    class Meta:
        verbose_name = _("customer concept")
        verbose_name_plural = _("customer concepts")

    def clean(self):
        if not Customer.objects.filter(
            organization_id__in=[self.organizer_id],
        ).exists():
            msg = _("This is not one of your customers")
            raise ValidationError({"customer": msg})

        super().clean()

    def save(self, *args, **kwargs):
        if isinstance(self.customer, B2BCustomer):
            self.segment = Concept.SegmentType.B2B
        else:
            self.segment = Concept.SegmentType.B2C
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.customer and self.name:
            return f"{self.name} - {self.customer}"
        if self.customer:
            return f"{self.customer}"

        return super().__str__()


class ConceptPriceMatrix(AdminLinkMixin):
    concept = models.ForeignKey(
        Concept,
        verbose_name=_(
            "concept",
        ),
        on_delete=models.CASCADE,
        related_name="price_matrixes",
        null=False,
        blank=False,
    )
    price_matrix = models.OneToOneField(
        "payments.PriceMatrix",
        verbose_name=_(
            "price matrix",
        ),
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    valid_from = models.DateTimeField(
        verbose_name=_(
            "valid from",
        ),
        null=True,
        blank=True,
    )
    valid_till = models.DateTimeField(
        verbose_name=_(
            "valid till",
        ),
        null=True,
        blank=True,
    )


class Event(PolymorphicModel, NameField, AdminLinkMixin, PublicKeyField, CardModel):
    concept = models.ForeignKey(
        Concept,
        verbose_name=_(
            "concept",
        ),
        related_name="events",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    expected_number_of_guests = models.IntegerField(
        verbose_name=_(
            "expected number of guests",
        ),
        null=True,
        blank=True,
    )

    minimum_number_of_guests = models.IntegerField(
        verbose_name=_(
            "minimum number of guests",
        ),
        null=True,
        blank=True,
    )
    maximum_number_of_guests = models.IntegerField(
        verbose_name=_(
            "maximum number of guests",
        ),
        null=True,
        blank=True,
    )
    reserved_spots = models.IntegerField(
        verbose_name=_(
            "reserved spots",
        ),
        default=0,
        blank=True,
    )

    reservation_settings = models.ForeignKey(
        "reservations.EventReservationSettings",
        verbose_name=_(
            "reservation settings",
        ),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    event_reservation_payment_settings = models.ForeignKey(
        "payments.EventReservationPaymentSettings",
        verbose_name=_(
            "event reservation payment settings",
        ),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    allow_reservations = models.BooleanField(
        verbose_name=_(
            "allow reservations",
        ),
        default=True,
    )

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")

    @property
    def organizer(self):
        if self.concept and self.concept.organizer:
            return self.concept.organizer
        return None

    @property
    def has_unlimited_spots(self):
        return self.maximum_number_of_guests is None

    @property
    def is_full(self):
        logger.debug("Checking if the event is full...")
        if self.has_unlimited_spots:
            logger.debug("Event has unlimited spots, so it's not full")
            return False

        result = self.free_spots == 0
        if result:
            logger.debug("Event is full")
        else:
            logger.debug("Event is not full")
        return result

    @property
    def free_spots(self):
        if self.has_unlimited_spots:
            return _("∞")

        logger.debug(
            "Max guests of event (%s): %s",
            self.id,
            self.maximum_number_of_guests,
        )

        if hasattr(self, "reserved_spots") and self.reserved_spots is not None:
            logger.debug("calculating the free spots")
            the_result = self.maximum_number_of_guests - self.reserved_spots
            if the_result <= 0:
                logger.debug("no free spots")
                return 0
            logger.debug("free spots: %s", the_result)
            return the_result

        logger.info("""We dont know how much reserved spots,
            so we don't know how to calculated the free spots""")  # pragma: no cover

        logger.debug("returning maximum number of guests")  # pragma: no cover
        return self.maximum_number_of_guests  # pragma: no cover

    def get_reserved_spots(self):
        logger.debug("calculating the reserved spots")
        number_of_reserved_spots = sum(
            r.total_amount for r in self.reservations.all() if r.is_confirmed
        )
        logger.debug("Number of reserved spots: %s", number_of_reserved_spots)
        return number_of_reserved_spots

    @property
    def free_percentage(self):
        if self.reserved_percentage < MAX_PERCENTAGE:
            return MAX_PERCENTAGE - self.reserved_percentage
        return 0

    @property
    def reserved_percentage(self):
        logger.debug("calculating the reserved percentage")
        if (
            hasattr(self, "reserved_spots")
            and self.reserved_spots is not None
            and self.maximum_number_of_guests is not None
        ):
            the_result = (
                self.reserved_spots / self.maximum_number_of_guests * MAX_PERCENTAGE
            )
            if the_result <= MAX_PERCENTAGE:
                return the_result
            return MAX_PERCENTAGE
        return 0  # pragma: no cover

    @property
    def over_reserved_spots(self):
        if self.reserved_percentage >= MAX_PERCENTAGE:
            return (self.maximum_number_of_guests - self.reserved_spots) * -1

        return 0

    @property
    def current_price_matrix(self):
        return self.concept.current_price_matrix

    @property
    def applicable_reservation_settings(self):
        logger.setLevel(logging.DEBUG)
        logger.debug("Checking for applicable reservation settings")
        if self.reservation_settings:
            return self.reservation_settings

        if self.concept and self.concept.reservation_settings:
            return self.concept.reservation_settings

        logger.info("No applicable reservation settings found")
        return None

    @property
    def applicable_event_reservation_payment_settings(self):
        if self.event_reservation_payment_settings:
            return self.event_reservation_payment_settings

        if self.concept and self.concept.event_reservation_payment_settings:
            return self.concept.event_reservation_payment_settings

        return None

    @property
    def show_progress_bar(self):
        logger.debug("Checking if progress bar needs to be shown")
        if self.applicable_reservation_settings is None:
            logger.debug("No because we do not have settings")
            return False

        if self.applicable_reservation_settings.always_show_progress_bar:
            logger.debug("Always show progress bar from settings")
            return True

        show_progress_bar_treshold = self.applicable_reservation_settings.show_progress_bar_when_x_percentage_reached  # noqa: E501
        if show_progress_bar_treshold is None:
            logger.debug("no because we do not have any treshold")
            return False

        reserved_percentage = self.reserved_percentage
        logger.debug("show progress bar treshold: %s", show_progress_bar_treshold)
        logger.debug("reserved capacity: %s", reserved_percentage)
        return show_progress_bar_treshold <= reserved_percentage

    @property
    def warnings(self):
        return [_("yay, there are no warnings")]

    def has_capacity_for(self, an_object):
        if an_object is None:
            logger.warning("We cannot calculat the capacity if the object is None")
            return False

        logger.debug("Checking if the event has capacity for: %s", an_object)
        if self.has_unlimited_spots:
            logger.debug("Event has unlimited spots, so it has capacity")
            return True

        if self.is_full:
            logger.debug("Event is full, so it has no capacity")
            return False

        if isinstance(an_object, Reservation):
            reservation = an_object
            if reservation.total_amount is None:
                msg = "Reservation amount cannot be None, if you would like to calculate the capacity"  # noqa: E501
                raise ValueError(msg)
            if reservation.total_amount == 0:
                logger.debug("Reservation amount is 0, so it has capacity")
                return True
            result = reservation.total_amount < self.free_spots
            logger.debug("Final capacity result: %s", result)
            return result
        return False

    def add_reserved_spots(self, the_amount):
        self.reserved_spots += the_amount
        self.save(update_fields=["reserved_spots"])

    def latest_updates(self):
        return self.updates.filter(
            Q(visible_from__gte=ITS_NOW, visible_till__lte=ITS_NOW)
            | Q(visible_till__isnull=True),
        ).order_by("-created_at")


class SingleEvent(Event, CateringField):
    class STATUS(models.TextChoices):
        UPCOMING = "UPCOMING", _("upcoming")
        ONGOING = "ONGOING", _("ongoing")
        ENDED = "ENDED", _("ended")
        UNKNOWN = "UNKNOWN", _("unknown")

    catering = models.ForeignKey(
        "catering.Catering",
        verbose_name=_(
            "catering",
        ),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "EventMix",
        verbose_name=_(
            "parent",
        ),
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )
    show_in_ongoing_events = models.BooleanField(
        verbose_name=_(
            "show in ongoing events",
        ),
        default=True,
    )
    starting_at = models.DateTimeField(
        verbose_name=_(
            "starting at",
        ),
        null=True,
    )
    ending_on = models.DateTimeField(
        verbose_name=_(
            "ending on",
        ),
        null=True,
    )
    duplicator = models.ForeignKey(
        "EventDuplicator",
        verbose_name=_(
            "duplicator",
        ),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
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
        ordering = ["starting_at"]

    def __str__(self):
        if self.concept and self.concept.name and self.starting_at:
            return f"{self.concept.name} {self.starting_at.date()}"

        if self.name:
            return f"{self.name}"

        return super().__str__()  # pragma: no cover

    @property
    def status(self):
        return self.get_status()

    def get_status(self, its_now=None):
        if its_now is None:
            its_now = ITS_NOW

        starting_at = self.starting_at
        ending_on = self.ending_on
        logger.debug("Starting at: %s", starting_at)
        logger.debug("It's now: %s", its_now)
        logger.debug("Ending on: %s", ending_on)

        if starting_at and ending_on is None and starting_at > its_now:
            return SingleEvent.STATUS.UPCOMING

        if starting_at and ending_on and starting_at > its_now:
            return SingleEvent.STATUS.UPCOMING

        if ending_on and its_now > ending_on:
            return SingleEvent.STATUS.ENDED

        if starting_at and ending_on and ending_on < its_now:
            return SingleEvent.STATUS.ENDED  # pragma: no cover

        if starting_at and ending_on and starting_at < its_now < ending_on:
            return SingleEvent.STATUS.ONGOING

        return SingleEvent.STATUS.UNKNOWN

    @property
    def reservations_closed_on(self):
        starting_datetime = self.starting_at
        if starting_datetime is None:
            return None

        if self.applicable_reservation_settings:
            if (
                self.applicable_reservation_settings.close_reservation_interval
                == EventReservationSettings.CloseReservationInterval.AT_START
            ):
                return self.starting_at

            if (
                self.applicable_reservation_settings.close_reservation_interval
                == EventReservationSettings.CloseReservationInterval.WHEN_ENDED
            ):
                return self.ending_on

            amount = self.applicable_reservation_settings.close_reservation_time_amount
            interval = self.applicable_reservation_settings.close_reservation_interval
            starting_datetime = self.starting_at

            return starting_datetime - relativedelta(**{interval: amount})

        return None

    @property
    def is_open_for_reservations(self):
        logger.debug("Checking if the reservations are open...")
        if self.applicable_reservation_settings is None:
            logger.debug("No reservations settings")
            return False

        if self.allow_reservations is False:
            logger.debug("Reservations are not allowed")
            return False

        if self.allow_reservations and self.reservations_closed_on is None:
            return True

        logger.debug("Time based checking if the reservations are open.")
        return self.reservations_closed_on >= ITS_NOW

    @property
    def reservations_are_closed(self):
        logger.debug("Checking if the reservations are closed...")
        if self.allow_reservations is False:
            logger.debug("Reservations are not allowed")
            return True

        if self.allow_reservations and self.reservations_closed_on is None:
            return False

        logger.debug("Time based checking if the reservations are closed.")
        return self.reservations_closed_on <= ITS_NOW

    @property
    def applicable_reservation_settings(self):
        if self.allow_reservations is False:
            return None

        if self.reservation_settings:
            return self.reservation_settings

        if self.concept and self.concept.reservation_settings:
            return self.concept.reservation_settings

        return None

    @property
    def applicable_catering(self):
        if self.catering:
            return self.catering

        if self.concept and self.concept.catering:
            return self.concept.catering

        return None


class EventMix(SingleEvent):
    class Meta:
        verbose_name = _("mix of events")
        verbose_name_plural = _("mix of events")

    def public_events(self):
        return self.children.all().order_by("starting_at")


class DanceEvent(SingleEvent):
    class Meta:
        verbose_name = _("dance event")
        verbose_name_plural = _("dance events")


class StayOver(SingleEvent):
    class Meta:
        verbose_name = _("stay over")
        verbose_name_plural = _("stay overs")


class BirthdayEvent(SingleEvent):
    ICON = "cake"

    class Meta:
        verbose_name = _("birthday")
        verbose_name_plural = _("birthdays")

    @property
    def warnings(self):
        warnings = []
        if self.attendees.count() == 0:
            warnings.append(_("please add at least the birthday person to your guests"))
        elif (
            self.attendees.filter(
                attendeerole__role=AttendeeRole.RoleType.BIRTHDAY_PERSON,
            ).count()
            == 0
        ):
            warnings.append(_("please add the birthday person to your guests"))
        return warnings


class WeddingEvent(SingleEvent):
    ICON = "cake"

    class Meta:
        verbose_name = _("wedding")
        verbose_name_plural = _("weddings")

    @property
    def warnings(self):
        minimum_attendees = 2
        warnings = []
        if self.attendees.count() < minimum_attendees:
            warnings.append(_("please add at least the couple to your guests"))
        elif (
            self.attendees.filter(
                attendees__role__in=[
                    AttendeeRole.RoleType.GROOM,
                    AttendeeRole.RoleType.BRIDE,
                ],
            ).count()
            == 0
        ):
            warnings.append(_("please add the groom or bride to your guests"))
        return warnings


class DinnerEvent(SingleEvent):
    ICON = "local_dining"

    class Meta:
        verbose_name = _("dinner")
        verbose_name_plural = _("dinners")

    @property
    def warnings(self):
        warnings = []
        if self.catering is None:
            warnings.append(_("your event has no catering yet"))
            return warnings

        if not self.catering.has_dinner_menu:
            warnings.append(_("your catering does not have a dinner menu"))

        return warnings


class LunchEvent(SingleEvent):
    ICON = "local_dining"

    class Meta:
        verbose_name = _("lunch")
        verbose_name_plural = _("lunches")

    @property
    def warnings(self):
        warnings = []
        if self.catering is None:
            warnings.append(_("your event has no catering yet"))
            return warnings

        if not self.catering.has_lunch_menu:
            warnings.append(_("your catering does not have a lunch menu"))

        return warnings


class MeetingEvent(SingleEvent):
    ICON = "local_dining"

    class Meta:
        verbose_name = _("meeting")
        verbose_name_plural = _("meetings")


class BreakfastEvent(SingleEvent):
    ICON = "local_dining"

    class Meta:
        verbose_name = _("breakfast")
        verbose_name_plural = _("breakfasts")

    @property
    def warnings(self):
        warnings = []
        if self.catering is None:
            warnings.append(_("your event has no catering yet"))
            return warnings

        if not self.catering.has_dinner_menu:
            warnings.append(_("your catering does not have a dinner menu"))

        return warnings


class LivePerformanceEvent(SingleEvent):
    ICON = "local_dining"

    class Meta:
        verbose_name = _("live performance")
        verbose_name_plural = _("live performances")


class PresentationEvent(SingleEvent):
    ICON = "local_dining"

    class Meta:
        verbose_name = _("presentation")
        verbose_name_plural = _("presentations")


class BrunchEvent(SingleEvent):
    ICON = "local_dining"

    class Meta:
        verbose_name = _("brunch")
        verbose_name_plural = _("brunches")

    @property
    def warnings(self):
        warnings = []
        if self.catering is None:
            warnings.append(_("your event has no catering yet"))
            return warnings

        if not self.catering.has_brunch_menu:
            warnings.append(_("your catering does not have a brunch menu"))

        return warnings


class TeamBuildingEvent(SingleEvent):
    ICON = "group"

    class Meta:
        verbose_name = _("team building")
        verbose_name_plural = _("team buildings")


class CeremonyEvent(SingleEvent):
    ICON = "visibility"

    class Meta:
        verbose_name = _("ceremony event")
        verbose_name_plural = _("ceremony events")


class ReceptionEvent(SingleEvent):
    ICON = "wc"

    class Meta:
        verbose_name = _("reception")
        verbose_name_plural = _("receptions")


class ClosingEvent(SingleEvent):
    ICON = "hotel"

    class Meta:
        verbose_name = _("closing")
        verbose_name_plural = _("closings")


class BreakEvent(SingleEvent):
    ICON = "pause"

    class Meta:
        verbose_name = _("break")
        verbose_name_plural = _("breaks")


class EventDuplicator(models.Model):  # noqa: DJ008
    class DuplicateInterval(models.TextChoices):
        EVERY_DAY = "EVERY_DAY", _("every AMOUNT day")
        EVERY_WEEK = "EVERY_WEEK", _("every AMOUNT week")
        EVERY_MONTH = "EVERY_MONTH", _("every AMOUNT month")
        EVERY_YEAR = "EVERY_YEAR", _("every AMOUNT year")

    event = models.ForeignKey(
        SingleEvent,
        verbose_name=_(
            "event",
        ),
        on_delete=models.CASCADE,
        null=True,
    )
    from_date = models.DateField(
        verbose_name=_(
            "from date",
        ),
        null=True,
        blank=True,
        help_text=_(
            "as starting date, we automatically take the starting datetime of the event",  # noqa: E501
        ),
        editable=False,
    )
    target_date = models.DateField(
        verbose_name=_(
            "to date",
        ),
        null=True,
    )
    amount = models.PositiveIntegerField(
        verbose_name=_(
            "amount",
        ),
        default=1,
        null=True,
    )
    every_interval = models.CharField(
        verbose_name=_(
            "every interval",
        ),
        max_length=50,
        choices=DuplicateInterval.choices,
        default=DuplicateInterval.EVERY_WEEK,
    )
    events_created = models.PositiveIntegerField(
        verbose_name=_(
            "events created",
        ),
        default=0,
        editable=False,
    )

    def duplicate(self):  # noqa: C901, PLR0912, PLR0915
        logger.info("Duplicating single event from duplicator: %s", self.pk)
        if self.event is None:
            msg = _("please choose your event to duplicate")
            raise ValueError(msg)

        if self.target_date is None:
            msg = _("please set your target date")
            raise ValueError(msg)

        self.from_date = self.event.starting_at.date()

        if self.target_date <= self.from_date:
            msg = _(
                "target date must be higher than the starting date of the event: %s",
                self.from_date,
            )
            raise ValueError

        event = self.event
        if event.starting_at is None:
            msg = _("we cannot duplicate an event witout starting date or time")
            raise ValueError(msg)

        if event.ending_on is None:
            msg = _("we cannot duplicate an event witout ending date or time")
            raise ValueError(msg)

        match self.every_interval:
            case self.DuplicateInterval.EVERY_DAY:
                self.interval = "days"

            case self.DuplicateInterval.EVERY_WEEK:
                self.interval = "weeks"

            case self.DuplicateInterval.EVERY_MONTH:
                self.interval = "months"

            case self.DuplicateInterval.EVERY_YEAR:
                self.interval = "years"

        time_interval = relativedelta(**{self.interval: self.amount})
        new_starting_datetime = datetime.datetime.combine(
            self.from_date + time_interval,
            event.starting_at.time(),
        )
        new_ending_datetime = datetime.datetime.combine(
            event.ending_on.date() + time_interval,
            event.ending_on.time(),
        )

        self.events_created = 0
        while new_starting_datetime.date() <= self.target_date:
            if SingleEvent.objects.filter(
                concept_id=event.concept_id,
                starting_at=new_starting_datetime,
                ending_on=new_ending_datetime,
            ).exists():
                logger.info("Event already exists")
                new_starting_datetime = datetime.datetime.combine(
                    new_starting_datetime.date() + time_interval,
                    event.starting_at.time(),
                )
                new_ending_datetime = datetime.datetime.combine(
                    new_ending_datetime + time_interval,
                    event.ending_on.time(),
                )
                continue

            new_event = type(event)()
            skip_fields = [
                "danceevent",
                "birthdayevent",
                "weddingevent",
                "dinnerevent",
                "lunchevent",
                "meetingevent",
                "breakfastevent",
                "liveperformanceevent",
                "presentationevent",
                "brunchevent",
                "teambuildingevent",
                "ceremonyevent",
                "receptionevent",
                "closingevent",
                "breakevent",
            ]
            for field in event._meta.get_fields():  # noqa: SLF001
                if isinstance(event, SingleEvent) and field.name in skip_fields:
                    logger.info("skipping field: %s", field.name)
                    continue
                logger.debug("Copying field: %s", field.name)
                value = getattr(event, field.name, None)
                logger.debug("%s: %s", field.name, value)
                try:
                    setattr(new_event, field.name, value)
                except TypeError:
                    logger.warning("TypeError")
                except AttributeError:
                    logger.warning("AttributeError")
                except ValueError:
                    logger.warning("ValueError")
                except Exception:  # noqa: BLE001
                    logger.warning("Exception")
                logger.debug("Ready to copy next field")

            logger.debug("Removing IDS and PK")
            new_event.pk = None
            new_event.id = None
            new_event.public_key = uuid4()
            new_event.duplicator_id = self.pk
            new_event.starting_at = new_starting_datetime
            new_event.ending_on = new_ending_datetime
            logger.debug("Save with public key: %s", str(new_event.public_key))
            new_event.save()

            logger.info("New event id: %s", str(new_event.pk) + " saved")
            self.events_created += 1

            new_starting_datetime = datetime.datetime.combine(
                new_starting_datetime.date() + time_interval,
                event.starting_at.time(),
            )
            new_ending_datetime = datetime.datetime.combine(
                new_ending_datetime + time_interval,
                event.ending_on.time(),
            )

        self.save()
        logger.info("%s events created", str(self.events_created))


class EventAttendee(PolymorphicModel, AdminLinkMixin, PublicKeyField):
    event = models.ForeignKey(
        SingleEvent,
        verbose_name=_(
            "event",
        ),
        on_delete=models.CASCADE,
        related_name="attendees",
        null=True,
    )
    person = models.ForeignKey(
        "hr.Person",
        verbose_name=_(
            "person",
        ),
        on_delete=models.CASCADE,
        related_name="events",
        null=True,
    )
    checked_in_at = models.DateTimeField(
        verbose_name=_(
            "checked in at",
        ),
        null=True,
        blank=True,
    )
    checked_out_at = models.DateTimeField(
        verbose_name=_(
            "checked out at",
        ),
        null=True,
        blank=True,
    )


class EventFloor(AdminLinkMixin):
    event = models.ForeignKey(
        Event,
        verbose_name=_(
            "event",
        ),
        on_delete=models.CASCADE,
        null=True,
    )
    floor = models.ForeignKey(
        "buildings.Floor",
        verbose_name=_(
            "floor",
        ),
        on_delete=models.CASCADE,
        null=True,
    )
    floor_layout = models.ForeignKey(
        "buildings.FloorLayout",
        verbose_name=_(
            "floor layout",
        ),
        on_delete=models.CASCADE,
        null=True,
    )


class AttendeeRole(AdminLinkMixin):
    class RoleType(models.TextChoices):
        ORGANIZER = "ORGANIZER", _("organizer")
        STAFF = "STAFF", _("staff")
        VIP = "VIP", _("vip")
        BRIDE = "BRIDE", _("bride")
        GROOM = "GROOM", _("groom")
        BIRTHDAY_PERSON = "BIRTHDAY_PERSON", _("birthday person")
        WEDDING_ANNIVERSARY = "WEDDING_ANNIVERSARY", _("wedding anniversary")
        DJ = "DJ", _("dj")
        ARTIST = "ARTIST", _("artist")
        PHOTOGRAPHER = "PHOTOGRAPHER", _("photographer")
        TECHNICIAN = "TECHNICIAN", _("technician")
        COOK = "COOK", _("cook")
        CATERER = "CATERER", _("caterer")
        SPEAKER = "SPEAKER", _("speaker")
        SECURITY_GUARD = "SECURITY_GUARD", _("security guard")
        STEWARD = "STEWARD", _("steward")
        PARKING_ASSISTANT = "PARKING_ASSISTANT", _("parking assistant")
        OTHER = "OTHER", _("other")

    role = models.CharField(
        verbose_name=_(
            "role",
        ),
        max_length=50,
        choices=RoleType.choices,
        default="",
        blank=False,
    )
    event_attendee = models.ForeignKey(
        EventAttendee,
        verbose_name=_(
            "event attendee",
        ),
        on_delete=models.CASCADE,
        null=True,
    )

    from_organization = models.ForeignKey(
        "organizations.Organization",
        verbose_name=_(
            "from organization",
        ),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    comments = models.TextField(
        verbose_name=_(
            "comments",
        ),
        default="",
        blank=True,
    )

    class Meta:
        verbose_name = _("attendee role")
        verbose_name_plural = _("attendee roles")


class EventUpdate(PolymorphicModel, LogInfoFields, AdminLinkMixin):
    class InformType(models.TextChoices):
        NOBODY = "NOBODY", _("nobody")
        ALL_GUESTS = "ALL_GUESTS", _("all guests")
        ALL_RESERVATION_REQUESTERS = (
            "ALL_RESERVATION_REQUESTERS",
            _("all reservation requesters"),
        )

    combined_choices = InformType.choices + AttendeeRole.RoleType.choices

    event = models.ForeignKey(
        Event,
        related_name="updates",
        on_delete=models.CASCADE,
        null=True,
    )
    inform = models.CharField(
        verbose_name=_(
            "inform",
        ),
        max_length=50,
        choices=combined_choices,
        default=InformType.NOBODY,
        help_text=_("who do we need to inform"),
    )
    notification = GenericRelation(
        "notifications.Notification",
        related_query_name="reservation_updates",
        content_type_field="about_content_type",
        object_id_field="about_object_id",
    )


class EventMessage(EventUpdate):
    title = models.CharField(verbose_name=_("title"), default="", blank=False)
    message = models.TextField(verbose_name=_("message"), default="", blank=False)
    visible_from = models.DateTimeField(
        verbose_name=_(
            "visible from",
        ),
        null=True,
    )
    visible_till = models.DateTimeField(
        verbose_name=_(
            "visible till",
        ),
        null=True,
        blank=True,
    )
