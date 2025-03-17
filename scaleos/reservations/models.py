import logging

from allauth.account.models import EmailAddress
from allauth.account.models import EmailConfirmation
from disposable_email_domains import blocklist
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from email_validator import EmailNotValidError
from email_validator import validate_email
from moneyed import EUR
from moneyed import Money
from polymorphic.models import PolymorphicModel

from scaleos.core.tasks import send_custom_templated_email
from scaleos.reservations.tasks import send_reservation_confirmation
from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import ITS_NOW
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.models import CardModel
from scaleos.users.models import User

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
        TO_BE_CONFIRMED_BY_REQUESTER = (
            "TO_BE_CONFIRMED_BY_REQUESTER",
            _(
                "to be confirmed by requester",
            ),
        )
        TO_BE_CONFIRMED_BY_ORGANIZATION = (
            "TO_BE_CONFIRMED_BY_ORGANIZATION",
            _(
                "to be confirmed by organization",
            ),
        )
        WAITING_FOR_PAYMENT = "WAITING_FOR_PAYMENT", _("waiting for payment")
        PARTIALLY_PAID = "PARTIALLY_PAID", _("partially paid")
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
    requester_confirmed_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_(
            """the moment the reservation is verified
            by the user who made the reservation""",
        ),
    )
    organization_confirmed_on = models.DateTimeField(
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
    payment_request = models.OneToOneField(
        "payments.PaymentRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
    def total_price_vat_included(self):
        total_price = Money(0, EUR)
        for line in self.lines.all():
            total_price += line.total_price_vat_included

        return total_price

    @property
    def total_amount(self):
        the_result = self.lines.all().aggregate(total=Sum("amount"))["total"]
        if the_result:
            return the_result

        return 0

    @property
    def verified_email_address(self):
        if self.user:
            try:
                return EmailAddress.objects.get(
                    email=self.user.email,
                    verified=True,
                ).email
            except EmailAddress.DoesNotExist:
                return None

        return None  # pragma: no cover

    @property
    def status(self):
        if self.finished_on is None:
            return self.STATUS.IN_PROGRESS
        if self.requester_confirmed_on is None:
            return self.STATUS.TO_BE_CONFIRMED_BY_REQUESTER
        if self.organization_confirmed_on is None:
            return self.STATUS.TO_BE_CONFIRMED_BY_ORGANIZATION
        if self.payment_request:
            if self.payment_request.payments.count() == 0:
                return self.STATUS.WAITING_FOR_PAYMENT
            if not self.payment_request.fully_paid:
                return self.STATUS.PARTIALLY_PAID

        return self.STATUS.UNKNOWN  # pragma: no cover

    def finish(self, request, confirmation_email_address):
        if self.finished_on:
            logger.warning("The reservation %s is already finished", self.pk)
            return False

        if isinstance(self, EventReservation):
            if self.total_amount == 0:
                msg = _("for an event reservation, you need at least one person")
                logger.warning(msg)
                raise ValidationError(msg)

        logger.info("checking email address: %s", confirmation_email_address)
        try:
            # Check that the email address is valid. Turn on check_deliverability
            # for first-time validations like on account creation pages (but not
            # login pages).
            confirmation_email_address = validate_email(
                confirmation_email_address,
                check_deliverability=True,
            )

            # After this point, use only the normalized form of the email address,
            # especially before going to a database query.
            confirmation_email_address = confirmation_email_address.normalized

        except EmailNotValidError as e:
            # The exception message is human-readable explanation of why it's
            # not a valid (or deliverable) email address.
            raise ValidationError(e) from EmailNotValidError

        email_domain = confirmation_email_address.split("@")[1]
        logger.debug("checking if email domain is blacklisted")
        if email_domain in blocklist:
            logger.warning("The email domain is blacklisted: %s", email_domain)
            raise ValidationError(_("this email address is blacklisted"))

        user, user_created = User.objects.get_or_create(
            email=confirmation_email_address,
        )

        if user_created:
            user.username = confirmation_email_address.split("@")[0]
            email_address, email_created = EmailAddress.objects.get_or_create(
                user=user,
                email=confirmation_email_address,
                primary=True,
            )
            if email_created:
                email_confirmation = EmailConfirmation.create(email_address)
                logger.info("new user created for a reservation")
                send_custom_templated_email(
                    request,
                    email_confirmation,
                    reservation=self,
                )

        self.user_id = user.pk
        self.finished_on = ITS_NOW

        if request and request.user.is_authenticated:
            self.created_by_id = request.user.pk

            if user.pk == request.user.pk:
                logger.info(
                    "The requester for the event is the same as the loggedin user",
                )
                self.requester_confirm()

        self.save()
        return True

    @property
    def organization_confirmed(self):
        return self.organization_confirmed_on is not None

    def organization_confirm(self):
        if self.organization_confirmed_on:
            logger.info(
                "The reservation %s is already confirmed by the organization",
                self.pk,
            )
            return False

        the_now = ITS_NOW
        logger.info("Organization confirmed on: %s", the_now)
        self.organization_confirmed_on = the_now
        self.save()
        self.update_payment_request()
        send_reservation_confirmation.delay(self.id)
        return True

    @property
    def requester_confirmed(self):
        return self.requester_confirmed_on is not None

    def requester_confirm(self):
        if self.requester_confirmed_on:
            logger.info(
                "The reseravtion %s is already confirmed by the requester",
                self.pk,
            )
            return False

        the_now = ITS_NOW
        logger.info("Requester confirmed on: %s", the_now)
        self.requester_confirmed_on = the_now
        self.save()
        return True

    def update_payment_request(self):
        from scaleos.payments.models import PaymentRequest
        from scaleos.payments.models import Price

        if self.payment_request is None:
            payment_request = PaymentRequest.objects.create()
            self.payment_request_id = payment_request.pk
            self.save()
        else:
            payment_request = PaymentRequest.objects.get(id=self.payment_request_id)

        if payment_request.to_pay is None:
            price = Price.objects.create(
                current_price=self.total_price_vat_included,
                includes_vat=True,
            )
            payment_request.to_pay_id = price.pk
            payment_request.save()
        else:
            price = Price.objects.get(id=payment_request.to_pay.pk)
            price.current_price = self.total_price_vat_included
            price.includes_vat = True
            price.save()
            payment_request.to_pay_id = price.pk
            payment_request.save()


class EventReservation(Reservation):
    event = models.ForeignKey(
        "events.Event",
        related_name="reservations",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )


class EventReservationSettings(AdminLinkMixin):
    class CloseReservationInterval(models.TextChoices):
        SECONDS = "seconds", _("seconds")
        MINUTES = "minutes", _("minutes")
        HOURS = "hours", _("hour")
        DAYS = "days", _("days")
        WEEKS = "weeks", _("weeks")
        MONTHS = "months", _("months")
        YEARS = "years", _("years")
        AT_START = "at_start", _("at start")
        WHEN_ENDED = "on_end", _("when ended")

    minimum_persons_per_reservation = models.IntegerField(
        null=True,
        blank=False,
        default=1,
    )
    maximum_persons_per_reservation = models.IntegerField(
        null=True,
        blank=False,
        default=30,
    )
    maximum_reservations_in_waitlist = models.IntegerField(
        null=True,
        blank=False,
        default=60,
    )

    close_reservation = models.IntegerField(null=True, blank=False, default=2)
    close_reservation_interval = models.CharField(
        max_length=50,
        choices=CloseReservationInterval.choices,
        default=CloseReservationInterval.DAYS,
        blank=True,
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
        except AttributeError as e:
            logger.warning(e)
        return None

    @property
    def total_price_vat_included(self):
        try:
            return self.amount * self.price_matrix_item.price.vat_included
        except AttributeError as e:
            logger.warning(e)
        return None

    @property
    def minimum_amount(self):
        if self.price_matrix_item and self.price_matrix_item.minimum_persons:
            return self.price_matrix_item.minimum_persons
        return 0

    @property
    def maximum_amount(self):
        if self.price_matrix_item and self.price_matrix_item.maximum_persons:
            return self.price_matrix_item.maximum_persons
        return 10
