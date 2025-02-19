import logging

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from moneyed import EUR
from moneyed import Money
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.models import CardModel

# Create your models here.
logger = logging.getLogger(__name__)


class Reservation(
    PolymorphicModel,
    AdminLinkMixin,
    LogInfoFields,
    PublicKeyField,
    CardModel,
):
    class STATUS(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", _("in progress")
        NEEDS_VERIFICATION = "NEEDS_VERIFICATION", _("needs verification")
        WAITING_FOR_PAYMENT = "WAITING_FOR_PAYMENT", _("waiting for payment")
        CONFIRMED = "CONFIRMED", _("confirmed")
        PARTIALLY_USED = "PARTIALLY_USED", _("partially used")
        USED = "USED", _("used")
        EVENT_OVER = "EVENT_OVER", _("event is over")

        ENDED = "ENDED", _("ended")
        UNKNOWN = "UNKNOWN", _("unknown")

    user = models.ForeignKey(
        get_user_model(),
        related_name="reservations",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    finished_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("the moment the reservation has been made"),
    )
    verified_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_(
            """the moment the reservation is verified
            by the user who made the reservation""",
        ),
    )
    confirmed_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("the moment the employee has confirmed the reservation"),
    )
    confirmation_mail_sent_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_(
            "the moment the confirmation email of the reservation has been sent",
        ),
    )

    class Meta:
        verbose_name = _("reservation")
        verbose_name_plural = _("reservations")

    @property
    def total_price(self):
        total_price = Money(0, EUR)
        for line in self.lines.all():
            total_price += line.total_price

        return total_price

    @property
    def total_amount(self):
        total_amount = 0
        for line in self.lines.all():
            total_amount += line.amount

        return total_amount

    @property
    def verified_email(self):
        try:
            return EmailAddress.objects.get(email=self.user.email, verified=True)
        except AttributeError:
            return None

    @property
    def status(self):
        if self.finished_on is None:
            return self.STATUS.IN_PROGRESS
        if self.verified_on is None:
            return _("needs verification")

        return _("unknown")


class EventReservation(Reservation):
    event = models.ForeignKey(
        "events.Event",
        related_name="reservations",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )


class ReservationLine(AdminLinkMixin, PublicKeyField):
    reservation = models.ForeignKey(
        Reservation,
        related_name="lines",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    amount = models.IntegerField(null=True, blank=False)
    price_matrix_item = models.ForeignKey(
        "payments.PriceMatrixItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )

    class Meta:
        ordering = ["pk"]

    @property
    def total_price(self):
        try:
            return self.amount * self.price_matrix_item.price.current_price
        except Exception as e:  # noqa: BLE001
            logger.warning(e)
        return None
