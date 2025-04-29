import logging

from admin_ordering.models import OrderableModel
from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.forms import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from localflavor.generic.countries.sepa import IBAN_SEPA_COUNTRIES
from localflavor.generic.models import IBANField
from moneyed import EUR
from moneyed import Money
from polymorphic.models import PolymorphicModel

from scaleos.payments.functions import ReferenceGenerator
from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import NameField
from scaleos.shared.fields import OriginFields
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import ITS_NOW
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.validators import validate_percentage

logger = logging.getLogger(__name__)


# Create your models here.


class PriceModel(LogInfoFields, AdminLinkMixin, PublicKeyField):
    vat = MoneyField(
        max_digits=15,
        decimal_places=2,
        default_currency="EUR",
        null=True,
        editable=False,
    )

    vat_included = MoneyField(
        max_digits=15,
        decimal_places=2,
        default_currency="EUR",
        null=True,
        editable=False,
    )

    vat_excluded = MoneyField(
        max_digits=15,
        decimal_places=2,
        default_currency="EUR",
        null=True,
        editable=False,
    )

    class Meta:
        abstract = True
        ordering = ["-created_on"]


class Price(PriceModel, LogInfoFields):
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="prices",
        on_delete=models.SET_NULL,
        null=True,
    )

    unique_origin_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    unique_origin_object_id = models.PositiveIntegerField(null=True, blank=True)
    unique_origin = GenericForeignKey(
        "unique_origin_content_type",
        "unique_origin_object_id",
    )

    class Meta:
        unique_together = ("unique_origin_content_type", "unique_origin_object_id")
        verbose_name = _("price")
        verbose_name_plural = _("prices")
        ordering = ["-created_on"]

    def create_history_record(self):
        item = PriceHistory.objects.create(
            created_by=self.created_by,
            vat=self.vat,
            vat_included=self.vat_included,
            vat_excluded=self.vat_excluded,
            price_id=self.id,
            modified_by_id=self.modified_by_id,
        )

        msg = f"new PriceHistory record created with id: {item.pk}"
        logger.debug(msg)

    def save(self, *args, **kwargs):
        create_history_record = False

        if self.pk is None:
            msg = "no history needs to be created, because it is a new price"
            logger.debug(msg)

        if (
            self.previous_price
            and self.vat_included != self.previous_price.vat_included
        ):
            msg = "The price changed, so make a historization record"
            logger.debug(msg)
            create_history_record = True

        super().save(*args, **kwargs)

        if self.previous_price is None:
            msg = "no historical record yet, create one..."
            logger.debug(msg)
            create_history_record = True

        if create_history_record:
            self.create_history_record()

    def __str__(self):
        logger.debug("Getting price string")
        """\xa0 is the non-breaking space (NBSP) character in Unicode"""
        str_vat = _("vat included")

        if hasattr(self, "vat_included") and self.vat_included:
            if self.vat_included.amount == 0:
                logger.debug("vat included amount is zero")
                return_string = f"{self.vat_included} {str_vat}".replace("\xa0", " ")
                logger.debug(return_string)
                return return_string

            return_string = f"{self.vat_included} ({str_vat})".replace(
                "\xa0",
                " ",
            )
            logger.debug(return_string)
            return return_string

        return_string = _("free")
        logger.debug(return_string)
        return f"{return_string}"

    @property
    def previous_price(self):
        if self.pk is None:
            logger.debug("save first")
            return None

        if self.history.count() >= 1:
            return self.history.order_by("-created_on").first()

        return None

    def multiply(self, amount):
        """As we do not want to change the origingal price in the database,
        we are creating a new price instance and return this"""
        logger.debug("Multiplying %s by %s", self, amount)
        multiplied_price = Price()

        multiplied_price.vat_included = self.vat_included * amount
        multiplied_price.vat_excluded = self.vat_excluded * amount
        multiplied_price.vat = (
            multiplied_price.vat_included - multiplied_price.vat_excluded
        )
        logger.debug("Returning multiplied price: %s", multiplied_price)
        return multiplied_price

    def plus(self, adding_price: "Price"):
        if not isinstance(adding_price, self.__class__):
            msg = f"Expected {self.model_name}, got {adding_price.model_name}"
            raise TypeError(
                msg,
            )

        if self.pk and adding_price.pk:
            for vat_line in adding_price.vat_lines.all():
                self.vat_lines.add(vat_line)

        if self.vat_included is None:
            self.vat_included = Money(0, EUR)

        if adding_price.vat_included is None:
            adding_price.vat_included = Money(0, EUR)

        if self.vat_excluded is None:
            self.vat_excluded = Money(0, EUR)

        if adding_price.vat_excluded is None:
            adding_price.vat_excluded = Money(0, EUR)

        self.vat_included += adding_price.vat_included
        self.vat_excluded += adding_price.vat_excluded
        self.vat = self.vat_included - self.vat_excluded
        return self

    def get_percentage(self, percentage):
        logger.debug("Getting percentage %s from %s", percentage, self)
        percentage_price = Price()
        percentage_price.vat_included = self.vat_included * percentage / 100
        percentage_price.vat_excluded = self.vat_excluded * percentage / 100
        percentage_price.vat = (
            percentage_price.vat_included - percentage_price.vat_excluded
        )

        logger.debug("Returning percentage price: %s", percentage_price)
        return percentage_price

    def recalculate_vat_totals(self):
        vat_included_total = sum(
            (line.vat_included for line in self.vat_lines.all() if line.vat_included),
            start=Money(0, EUR),
        )
        self.vat_included = vat_included_total

        vat_excluded_total = sum(
            (line.vat_excluded for line in self.vat_lines.all() if line.vat_excluded),
            start=Money(0, EUR),
        )
        self.vat_excluded = vat_excluded_total
        self.vat = vat_included_total - vat_excluded_total

        self.save(update_fields=["vat_included", "vat_excluded", "vat"])


class VATPriceLine(PriceModel):
    price = models.ForeignKey(
        Price,
        related_name="vat_lines",
        on_delete=models.SET_NULL,
        null=True,
    )
    input_price = MoneyField(
        max_digits=15,
        decimal_places=2,
        default_currency="EUR",
        null=True,
    )
    includes_vat = models.BooleanField(
        null=True,
    )
    vat_percentage = models.IntegerField(
        validators=[validate_percentage],
        null=True,
    )

    class Meta:
        ordering = ["-created_on"]
        verbose_name = _("VAT price line")
        verbose_name_plural = _("VAT price lines")

    def save(self, *args, **kwargs):
        self.set_vat_included()
        self.set_vat_excluded()
        self.set_vat()
        super().save(*args, **kwargs)

    def clean(self):
        if self.input_price is None or self.input_price.amount == 0:
            msg = _(
                "your input price may not be 0, otherwise it's free",
            )
            raise ValidationError({"input_price": msg})

        if self.vat_percentage is None:
            msg = _("please set your vat percentage")
            raise ValidationError({"vat_percentage": msg})
        if self.includes_vat is None:
            msg = _("does your price include VAT")
            raise ValidationError({"includes_vat": msg})

        super().clean()

    def vat_controles_ok(self) -> bool:
        logger.debug("doing vat controles")

        if self.input_price is None:
            msg = _("we cannot set the vat without an input price")
            logger.warning(msg)
            return False
        logger.debug("The input price is: %s", self.input_price)

        if self.vat_percentage is None:
            msg = _("we cannot set the vat without a vat percentage")
            raise ValueError(msg)
        logger.debug("The vat percentage is: %s", self.vat_percentage)

        if self.includes_vat is None:
            msg = _("we need to know if the input price contains vat or not")
            raise ValueError(msg)
        logger.debug("the input price contains vat? %s", self.includes_vat)

        logger.debug("vat controles passed.")
        return True

    def set_vat_excluded(self):
        logger.debug("setting vat excluded")
        if not self.vat_controles_ok():
            return

        if self.includes_vat:
            self.vat_excluded = self.input_price / (1 + self.vat_percentage / 100)
        else:
            self.vat_excluded = self.input_price

        logger.debug("vat excluded set to: %s", self.vat_excluded)

    def set_vat_included(self):
        logger.debug("setting vat included")
        if not self.vat_controles_ok():
            return

        if self.includes_vat:
            self.vat_included = self.input_price
        else:
            self.vat_included = self.input_price + self.input_price * (
                self.vat_percentage / 100
            )

        logger.debug("vat included set to: %s", self.vat_included)

    def set_vat(self):
        logger.debug("setting vat")
        if not self.vat_controles_ok():
            return

        if self.vat_included and self.vat_excluded:
            self.vat = self.vat_included - self.vat_excluded
            logger.info("vat set to: %s", self.vat)
        else:
            logger.warning(
                "vat included and vat included are None, \
                      so we cannot calculate the VAT",
            )


class PriceHistory(PriceModel):
    price = models.ForeignKey(
        Price,
        related_name="history",
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        ordering = ["-created_on"]


class PriceMatrix(
    PolymorphicModel,
    LogInfoFields,
    AdminLinkMixin,
    NameField,
    PublicKeyField,
):
    show_matrix_name_in_item_name = models.BooleanField(default=True)


class AgePriceMatrix(PriceMatrix):
    pass


class BulkPriceMatrix(PriceMatrix):
    pass


class PriceMatrixItem(PolymorphicModel, AdminLinkMixin, PublicKeyField, NameField):
    price = GenericRelation(
        Price,
        content_type_field="unique_origin_content_type",
        object_id_field="unique_origin_object_id",
    )

    @property
    def is_free(self):
        if self.price.first() is None:
            return True

        return self.price.first().vat_included.amount == 0

    @property
    def current_price(self):
        if self.price.first() is None:
            return Price(vat_included=Money(0, EUR))

        return self.price.first()


class AgePriceMatrixItem(PriceMatrixItem):
    age_price_matrix = models.ForeignKey(
        AgePriceMatrix,
        related_name="prices",
        on_delete=models.SET_NULL,
        null=True,
    )

    from_age = models.IntegerField(
        null=True,
        blank=True,
    )
    till_age = models.IntegerField(
        null=True,
        blank=True,
    )

    minimum_persons = models.IntegerField(
        null=True,
        blank=True,
        default=0,
    )
    maximum_persons = models.IntegerField(
        null=True,
        blank=True,
        default=30,
    )

    def __str__(self):
        year = _("year")
        prefix = ""
        if (
            self.age_price_matrix
            and self.age_price_matrix.show_matrix_name_in_item_name
            and self.age_price_matrix.name
        ):
            prefix = f"{self.age_price_matrix.name}"

        if self.name:
            prefix = f"{prefix} - {self.name}"

        price = self.current_price
        if self.is_free:
            price = _("free").title()

        if self.from_age and self.till_age:
            return (
                f"{prefix} ({self.from_age} {year} - {self.till_age} {year}): {price}"
            )
        if self.from_age:
            return f"{prefix} ({self.from_age} {year} - ... ): {price}"

        if self.till_age:
            return f"{prefix} (0 {year} - {self.till_age} {year}): {price}"

        return super().__str__()  # pragma: no cover


class BulkPriceMatrixItem(PriceMatrixItem, OrderableModel):
    bulk_price_matrix = models.ForeignKey(
        BulkPriceMatrix,
        related_name="prices",
        on_delete=models.SET_NULL,
        null=True,
    )

    from_number_of_items = models.IntegerField(
        verbose_name=_(
            "from number of items",
        ),
        null=True,
        blank=True,
        help_text="from number of items",
    )
    to_number_of_items = models.IntegerField(
        verbose_name=_(
            "to number of items",
        ),
        null=True,
        blank=True,
        help_text="to number of items",
    )
    amount = models.IntegerField(default=1, help_text="You get")

    class Meta(OrderableModel.Meta):
        verbose_name = _("bulk price matrix item")
        verbose_name_plural = _("bulk price matrix items")


class PaymentSettings(PolymorphicModel, AdminLinkMixin, LogInfoFields, PublicKeyField):
    organization = models.ForeignKey(
        "organizations.Organization",
        verbose_name=_(
            "organization",
        ),
        related_name="prepayment_settings",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )

    class Meta:
        verbose_name = _("payment settings")
        verbose_name_plural = _("payment settings")


class PaymentRequest(AdminLinkMixin, LogInfoFields, OriginFields, PublicKeyField):
    price = GenericRelation(
        Price,
        content_type_field="unique_origin_content_type",
        object_id_field="unique_origin_object_id",
    )
    to_person = models.ForeignKey(
        "hr.Person",
        verbose_name=_("to person"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    to_organization = models.ForeignKey(
        "organizations.Organization",
        verbose_name=_("to organization"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    payment_settings = models.ForeignKey(
        PaymentSettings,
        verbose_name=_(
            "payment settings",
        ),
        related_name="payments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    structured_reference_be = models.CharField(
        max_length=20,
        blank=True,
        editable=False,
    )
    structured_reference_sepa = models.CharField(
        max_length=25,  # "RF" + 2 digits + up to 21 characters
        null=True,
        unique=True,  # Important: references should be unique
        blank=True,  # Allow blank at first (can generate later)
        editable=False,  # Optional: hide in Django admin forms
    )

    @property
    def to_pay(self) -> Price | None:
        if self.price.first() is None:
            return None

        return self.price.first()

    @property
    def already_paid(self):
        if self.to_pay and self.to_pay.vat_included:
            result = self.get_paid_payments([self.to_pay.vat_included.currency.code])
            if result:
                return result
        return None

    def get_paid_payments(self, expected_currencies=None):
        grouped = self.payments.values(
            "paid_amount_currency",
        ).annotate(  # Group by currency
            already_paid=Coalesce(
                Sum("paid_amount"),
                Value(0),
                output_field=MoneyField(
                    max_digits=14,
                    decimal_places=2,
                ),  # <<< ADD THIS
            ),
        )

        result = {
            item["paid_amount_currency"]: Money(
                item["already_paid"],
                item["paid_amount_currency"],
            )
            for item in grouped
        }

        if expected_currencies:
            for currency_code in expected_currencies:
                if currency_code not in result:
                    result[currency_code] = Money(0, currency_code)

        return result

    @property
    def still_to_pay(self):
        return self.get_remaining_to_pay()

    def get_remaining_to_pay(self, expected_currencies=None):
        if self.to_pay and self.to_pay.vat_included:
            paid = self.get_paid_payments(expected_currencies=expected_currencies)

            requested_currency = self.to_pay.vat_included.currency.code

            paid_amount = paid.get(requested_currency, Money(0, requested_currency))

            remaining_amount = self.to_pay.vat_included - paid_amount

            return {requested_currency: remaining_amount}
        return None

    @property
    def fully_paid(self):
        if self.still_to_pay:
            if self.to_pay and self.to_pay.vat_included:
                to_pay = self.still_to_pay[
                    self.to_pay.vat_included.currency.code
                ].amount
                return to_pay <= 0.0
        return None

    @property
    def payment_methods(self):
        return self.to_organization.payment_methods.all()

    def save(self, *args, **kwargs):
        if not self.structured_reference_be:
            # Use the invoice number as base number
            self.structured_reference_be = (
                ReferenceGenerator.generate_structured_reference(
                    base_number=self.pk,
                    decorated=True,
                )
            )
        else:
            # Optional: validate manually if needed
            ReferenceGenerator.validate_structured_reference(
                self.structured_reference_be,
            )

        if not self.structured_reference_sepa:
            self.structured_reference_sepa = (
                ReferenceGenerator.generate_iso11649_reference(base_number=self.pk)
            )

        super().save(*args, **kwargs)

    def structured_reference_plain(self):
        """Returns plain numeric version (without slashes and +++)."""

        return ReferenceGenerator.to_plain(self.structured_reference_be)

    def __str__(self):
        return f"Payment Request #{self.pk}"

    def set_price_to_pay(self, price_to_pay: Price):
        logger.debug("setting price to pay")
        ct = ContentType.objects.get_for_model(
            PaymentRequest,
        )
        if self.to_pay is None:
            price_to_pay.unique_origin_content_type = ct
            price_to_pay.unique_origin_object_id = self.pk
            price_to_pay.save()
        else:
            logger.info("Updating price in payment request")
            price = Price.objects.get(
                unique_origin_content_type=ct,
                unique_origin_object_id=self.pk,
            )
            price.vat_included = price_to_pay.vat_included
            price.vat_excluded = price_to_pay.vat_excluded
            price.vat = price_to_pay.vat
            price.save()

    def apply_payment_settings(self):
        logger.info("Applying payment settings")
        from scaleos.reservations.models import EventReservation

        if self.payment_settings is None:
            logger.info("no payment settings to apply")
            return

        if isinstance(self.origin, EventReservation) and isinstance(
            self.payment_settings,
            EventReservationPaymentSettings,
        ):
            self.payment_settings.apply_payment_conditions(self.origin)
            return

        msg = _("%s has no %s", self.origin, self.payment_settings)
        raise NotImplementedError(msg)


class PaymentProposal(AdminLinkMixin, OriginFields, LogInfoFields):
    payment_request = models.ForeignKey(
        PaymentRequest,
        verbose_name=_(
            "payment request",
        ),
        related_name="payment_proposals",
        on_delete=models.SET_NULL,
        null=True,
    )
    price = models.OneToOneField(
        Price,
        verbose_name=_(
            "price",
        ),
        related_name="proposal",
        on_delete=models.CASCADE,
        null=True,
    )

    due_datetime = models.DateTimeField(
        verbose_name=_("due date & time"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("payment proposal")
        verbose_name_plural = _("payment proposals")


class Payment(
    PolymorphicModel,
    AdminLinkMixin,
    PublicKeyField,
    LogInfoFields,
    OriginFields,
):
    payment_request = models.ForeignKey(
        PaymentRequest,
        related_name="payments",
        on_delete=models.SET_NULL,
        null=True,
    )

    paid_amount = MoneyField(
        max_digits=15,
        decimal_places=2,
        default_currency="EUR",
        null=True,
        blank=True,
    )
    paid_on = models.DateTimeField(null=True, blank=True)


class EPCMoneyTransferPayment(Payment):
    from_iban = IBANField(include_countries=IBAN_SEPA_COUNTRIES, null=True, blank=True)


class EventReservationPaymentSettings(PaymentSettings):
    @property
    def example_conditions(self):
        return self.get_conditions_text(self.get_example_event_reservation())

    class Meta:
        verbose_name = _("event reservation payment settings")
        verbose_name_plural = _("event reservation payment settings")

    def get_conditions(self, event_reservation=None):
        logger.info("getting conditions")
        if event_reservation is None:
            msg = "we do not have an event reservation, so we cannot calculate the conditions."  # noqa: E501
            logger.info(msg)
            return None

        conditions = {}
        for current_condition in self.conditions.all():
            logger.info(current_condition)
            due_date = current_condition.get_due_date(event_reservation)
            if due_date is None:
                continue

            conditions[due_date] = str(current_condition)

        return dict(sorted(conditions.items()))

    def get_conditions_text(self, event_reservation=None):
        logger.info("getting conditions text")
        return_string = _("no conditions defined")
        the_conditions = self.get_conditions(event_reservation)
        if the_conditions is None or len(the_conditions) == 0:
            logger.debug(return_string)
            return return_string

        logger.info("we have conditions, preparing text")
        return_string = "<ul>"
        for idx, cond in enumerate(the_conditions):
            logger.info("handling condition %s", idx)
            return_string += f"<li>{the_conditions[cond]}</li>"

        return_string += "</ul>"
        return mark_safe(return_string)  # noqa: S308

    def __str__(self):
        return super().__str__()

    def get_example_event_reservation(self):
        from scaleos.reservations.models import EventReservation

        return EventReservation.objects.filter(
            organization_id=self.organization.pk,
        ).first()

    def apply_payment_conditions(self, event_reservation):
        logger.info("applying event reservation payment conditions")
        total_conditions = self.conditions.count()
        logger.info("total conditions: %s", total_conditions)
        for idx, cond in enumerate(self.conditions.all(), start=1):
            logger.info("handling condition %s", idx)
            requesting_price = cond.get_price(event_reservation)
            if requesting_price is None:
                logger.info("The condition is not applicable.")
                continue
            payment_proposal, created = PaymentProposal.objects.get_or_create(
                payment_request=event_reservation.payment_request,
                origin_content_type=ContentType.objects.get_for_model(cond),
                origin_object_id=cond.pk,
            )
            due_datetime = cond.get_due_date(event_reservation)
            logger.info("due date: %s", due_datetime)
            payment_proposal.due_datetime = due_datetime
            requesting_price.organization_id = self.organization.pk
            logger.info("requesting price: %s", requesting_price)
            requesting_price.save()
            payment_proposal.price_id = requesting_price.pk
            payment_proposal.save()


class PaymentCondition(PolymorphicModel, AdminLinkMixin, LogInfoFields):
    class ToBePaidInterval(models.TextChoices):
        SECONDS = "seconds", _("seconds")
        MINUTES = "minutes", _("minutes")
        HOURS = "hours", _("hour")
        DAYS = "days", _("days")
        WEEKS = "weeks", _("weeks")
        MONTHS = "months", _("months")
        YEARS = "years", _("years")

    to_be_paid_time_amount = models.IntegerField(
        null=True,
        default=5,
    )

    to_be_paid_interval = models.CharField(
        max_length=50,
        choices=ToBePaidInterval.choices,
        default=ToBePaidInterval.DAYS,
    )

    price = GenericRelation(
        Price,
        content_type_field="unique_origin_content_type",
        object_id_field="unique_origin_object_id",
    )

    is_warranty = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("payment condition")
        verbose_name_plural = _("payment conditions")
        ordering = ["-created_on"]


class EventReservationPaymentCondition(PaymentCondition):
    class PrepaymentType(models.TextChoices):
        FULL_PRICE = "FULL_PRICE", _("full price")
        FIXED_PRICE = "FIXED_PRICE", _("fixed price")
        FIXED_PRICE_PER_PERSON = (
            "FIXED_PRICE_PER_PERSON",
            _("fixed price per person"),
        )
        PERCENTAGE_OF_TOTAL_PRICE = (
            "PERCENTAGE_OF_TOTAL_PRICE",
            _("percentage of total price"),
        )
        REMAINING_PRICE = "REMAINING_PRICE", _("remaining price")

    class PaymentMoment(models.TextChoices):
        BEFORE_START_OF_EVENT = (
            "BEFORE_START_OF_EVENT",
            _("before the start of the event"),
        )
        AFTER_START_OF_EVENT = "AFTER_START_OF_EVENT", _("after the start of the event")
        BEFORE_END_OF_EVENT = "BEFORE_END_OF_EVENT", _("before the event ends")
        AFTER_END_OF_EVENT = "AFTER_END_OF_EVENT", _("after the event ended")
        AT_START_OF_EVENT = "AT_START_OF_EVENT", _("at the start of the event")
        AT_END_OF_EVENT = "AT_END_OF_EVENT", _("at the end of the event")
        AFTER_RESERVATION_CONFRIMATION = (
            "AFTER_RESERVATION_CONFRIMATION",
            _("after the reservation confirmation"),
        )

    event_reservation_payment_settings = models.ForeignKey(
        EventReservationPaymentSettings,
        verbose_name=_(
            "event reservation payment settings",
        ),
        related_name="conditions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    payment_moment = models.CharField(
        max_length=50,
        choices=PaymentMoment.choices,
        default=PaymentMoment.BEFORE_START_OF_EVENT,
    )

    prepayment_type = models.CharField(
        max_length=40,
        choices=PrepaymentType.choices,
        default=PrepaymentType.FIXED_PRICE,
    )

    only_when_group_exceeds = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("number of persons"),
    )

    percentage_of_total_price = models.DecimalField(
        null=True,
        blank=True,
        validators=[validate_percentage],
        max_digits=6,
        decimal_places=2,
    )

    class Meta:
        verbose_name = _("event reservation payment condition")
        verbose_name_plural = _("event reservation payment conditions")

    def clean(self):
        super().clean()  # Ensure parent validations are executed

        match self.prepayment_type:
            case self.PrepaymentType.PERCENTAGE_OF_TOTAL_PRICE:
                if (
                    self.percentage_of_total_price is None
                    or self.percentage_of_total_price <= 0
                ):
                    msg = _(
                        "you need to set a percentage when the payment type is set to percentage of total price",  # noqa: E501
                    )
                    raise ValidationError({"percentage_of_total_price": msg})

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation is run before saving
        super().save(*args, **kwargs)

    def __str__(self):
        str_to_be_paid = _("to be paid")
        payment_moment = self.get_payment_moment_display()

        starting_string = ""
        ending_string = f"{str_to_be_paid} {self.to_be_paid_time_amount} {self.to_be_paid_interval} {payment_moment}"  # noqa: E501

        match self.prepayment_type:
            case self.PrepaymentType.FULL_PRICE:
                starting_string = f"{_('full price')}"
            case self.PrepaymentType.REMAINING_PRICE:
                starting_string = f"{_('remaining price')}"
            case self.PrepaymentType.FIXED_PRICE:
                starting_string = f"{_('fixed price')}"
            case self.PrepaymentType.FIXED_PRICE_PER_PERSON:
                starting_string = f"{_('fixed price per person')}"
            case self.PrepaymentType.PERCENTAGE_OF_TOTAL_PRICE:
                percentage = self.percentage_of_total_price
                percentage_text = _("% of total price")
                starting_string = f"{percentage}{percentage_text}"

        if self.only_when_group_exceeds:
            ending_string += (
                " but only when group exceeds "
                + str(self.only_when_group_exceeds)
                + " persons"
            )

        return f"{starting_string} {ending_string}".capitalize()

    def get_example_event_reservation(self):
        logger.info("getting example event reservation")
        the_result = (
            self.event_reservation_payment_settings.get_example_event_reservation()
        )
        if the_result is None:
            msg = _(
                "We do not have any event reservation, so we are not able to calculate the price",  # noqa: E501
            )
            logger.warning(msg)
        return the_result

    @property
    def current_price(self):
        return self.price.first()

    def get_due_date(self, event_reservation):  # noqa: C901
        logger.info("Getting the due date of the event")
        if event_reservation is None:
            event_reservation = self.get_example_event_reservation()

        the_date = ITS_NOW
        before_the_event = True

        if not hasattr(event_reservation, "event") or event_reservation.event is None:
            logger.info("The event reservation has no event")
            return None

        event = event_reservation.event

        the_moment = self.payment_moment
        logger.info("To be paid on %s", the_moment)
        match the_moment:
            case self.PaymentMoment.AT_START_OF_EVENT:
                return event.starting_at
            case self.PaymentMoment.AT_END_OF_EVENT:
                return event.ending_on
            case self.PaymentMoment.BEFORE_START_OF_EVENT:
                the_date = event.starting_at
                before_the_event = True
            case self.PaymentMoment.AFTER_START_OF_EVENT:
                the_date = event.starting_at
                before_the_event = False
            case self.PaymentMoment.BEFORE_END_OF_EVENT:
                the_date = event.ending_on
                before_the_event = True
            case self.PaymentMoment.AFTER_END_OF_EVENT:
                the_date = event.ending_on
                before_the_event = False

        if the_date is None:
            logger.info("The date is NONE, so we cannot calculate the due date.")
            return None

        pay_interval = self.to_be_paid_interval
        pay_interval_amount = self.to_be_paid_time_amount
        logger.info(
            "To be paid %s %s relative to %s",
            pay_interval_amount,
            pay_interval,
            the_date,
        )

        if before_the_event:
            logger.info("The due date is before the event")
            due_date = the_date - relativedelta(
                **{self.to_be_paid_interval: self.to_be_paid_time_amount},
            )
            logger.info("The due date is %s", due_date)
            return due_date

        logger.info("The due date is after the event")
        due_date = the_date + relativedelta(
            **{self.to_be_paid_interval: self.to_be_paid_time_amount},
        )
        logger.info("The due date is %s", due_date)
        return due_date

    def get_price(self, event_reservation=None) -> Price | None:  # noqa: C901, PLR0911
        if event_reservation is None:
            event_reservation = self.get_example_event_reservation()

        if not hasattr(event_reservation, "event") or event_reservation.event is None:
            return None

        if self.condition_applicable(event_reservation) is False:
            return None

        match self.prepayment_type:
            case self.PrepaymentType.FULL_PRICE:
                logger.info("Full price condition")
                return event_reservation.get_total_price()
            case self.PrepaymentType.FIXED_PRICE:
                logger.info("Fixed price condition")
                if self.current_price is None:
                    return None
                return self.current_price
            case self.prepayment_type.FIXED_PRICE_PER_PERSON:
                logger.info("Fixed price per person condition")
                the_price = self.price.first()
                if the_price:
                    return the_price.multiply(event_reservation.total_amount)

            case self.PrepaymentType.PERCENTAGE_OF_TOTAL_PRICE:
                logger.info("Percentage of total price condition")
                if self.percentage_of_total_price is None:
                    return None
                return event_reservation.get_total_price().get_percentage(
                    self.percentage_of_total_price,
                )
            case self.PrepaymentType.REMAINING_PRICE:
                return self.get_remaining_price()

        return None

    def condition_applicable(self, event_reservation):
        condition_only_when_exceeding = self.only_when_group_exceeds
        if condition_only_when_exceeding:
            logger.info(
                "The condition should only be applied when exceeding %s persons",
                condition_only_when_exceeding,
            )
            group_is_x_persons = event_reservation.total_amount
            logger.info("The group has %s persons", group_is_x_persons)
            if group_is_x_persons is None or group_is_x_persons == 0:
                logger.info("The total amount of the reservation is 0 or None")
                return False

            if group_is_x_persons < condition_only_when_exceeding:
                return False
        return True

    def get_remaining_price(self, event_reservation):
        logger.debug("Remaining price condition")
        if event_reservation.payment_request is None:
            logger.info(
                "we cannot calculate the remaining price \
                    when teh payment request is None",
            )
            return None

        if event_reservation.payment_request.to_pay is None:
            logger.info(
                "we cannot calculate the remaining price \
                        if we do not know how much to pay",
            )
            return None

        if event_reservation.payment_request.already_paid is None:
            logger.info("Nothing is paid yet, returning the total price")
            return event_reservation.get_total_price()

        if event_reservation.payment_request.to_pay.vat_included is None:
            logger.info(
                "We do not know how much the price with VAT included is",
            )

        to_pay = event_reservation.payment_request.to_pay.vat_included
        needed_currency = (
            event_reservation.payment_request.to_pay.vat_included.currency.code
        )
        already_paid = event_reservation.payment_request.already_paid[needed_currency]

        if already_paid >= to_pay:
            logger.info("There is already more paid than needed")
            return Money(0, needed_currency)

        return to_pay - already_paid


class PaymentMethod(PolymorphicModel, AdminLinkMixin, LogInfoFields, PublicKeyField):
    class Meta:
        verbose_name = _("payment method")
        verbose_name_plural = _("payment methods")


class VoucherPaymentMethod(
    PaymentMethod,
):
    class Meta:
        verbose_name = _("voucher")
        verbose_name_plural = _("vouchers")


class EPCMoneyTransferPaymentMethod(PaymentMethod):
    iban = IBANField(include_countries=IBAN_SEPA_COUNTRIES, null=True, blank=False)

    class Meta:
        verbose_name = _("EPC money transfer")
        verbose_name_plural = _("EPC money transfer")


class CashPaymentMethod(PaymentMethod):
    class Meta:
        verbose_name = _("cash")
        verbose_name_plural = _("cash")
