import logging

from admin_ordering.models import OrderableModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import AdminLinkMixin

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

    vat_percentage = models.IntegerField(default=21)

    class Meta:
        abstract = True
        ordering = ["-created_on"]


class Price(PriceModel):
    current_price = MoneyField(
        max_digits=15,
        decimal_places=2,
        default_currency="EUR",
        null=True,
        blank=True,
    )

    includes_vat = models.BooleanField(default=True)

    def create_history_record(self):
        item = PriceHistory.objects.create(
            created_by=self.created_by,
            vat=self.vat,
            vat_included=self.vat_included,
            vat_excluded=self.vat_excluded,
            price_id=self.id,
        )

        msg = "new PriceHistory record created with id: %s", item.pk
        logger.debug(msg)

    def save(self, *args, **kwargs):
        self.vat_included = self.get_vat_included()
        self.vat_excluded = self.get_vat_excluded()
        self.vat = self.get_vat()
        if self.pk is None:
            msg = _("save first")
            logger.debug(msg)

        if (
            self.previous_price
            and self.vat_included != self.previous_price.vat_included
        ):
            msg = "The price changed"
            logger.debug(msg)
            self.create_history_record()

        if self.previous_price is None:
            msg = "no historical record yet, create one..."
            logger.debug(msg)
            self.create_history_record()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.current_price}"

    @property
    def previous_price(self):
        if self.pk is None:
            logger.debug("save first")
            return None

        if self.history.count() > 1:
            return self.history.all()[1]

        return None

    @property
    def text(self):
        if self.current_price is None:
            return _("free")

        if int(self.current_price.amount) == 0:
            return _("free")

        return str(self.current_price).replace("\xa0", "")

    def get_vat_excluded(self):
        if self.current_price is None:
            return None

        if not self.includes_vat:
            return self.current_price

        return self.current_price / (1 + self.vat_percentage / 100)

    def get_vat_included(self):
        if self.current_price is None:
            return None

        if self.includes_vat:
            return self.current_price

        return self.current_price + self.current_price * (self.vat_percentage / 100)

    def get_vat(self):
        if self.vat_included and self.vat_excluded:
            return self.vat_included - self.vat_excluded

        return None


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
    pass


class AgePriceMatrix(PriceMatrix):
    pass


class BulkPriceMatrix(PriceMatrix):
    pass


class PriceMatrixItem(PolymorphicModel, AdminLinkMixin, PublicKeyField):
    pass


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

    price = models.OneToOneField(
        Price,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        help_text="will pay",
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
        if (
            self.age_price_matrix
            and self.age_price_matrix.name
            and self.from_age
            and self.till_age
            and self.price
        ):
            return f"{self.age_price_matrix.name} \
({self.from_age}-{self.till_age}): {self.price.text}"
        if (
            self.age_price_matrix
            and self.age_price_matrix.name
            and self.from_age
            and self.price
        ):
            return (
                f"{self.age_price_matrix.name} ({self.from_age}-...): {self.price.text}"
            )

        if self.age_price_matrix and self.age_price_matrix.name and self.till_age:
            return (
                f"{self.age_price_matrix.name} (0-{self.till_age}): {_('free').title()}"
            )

        return super().__str__()  # pragma: no cover


class BulkPriceMatrixItem(PriceMatrixItem, OrderableModel):
    bulk_price_matrix = models.ForeignKey(
        BulkPriceMatrix,
        related_name="prices",
        on_delete=models.SET_NULL,
        null=True,
    )

    from_number_of_items = models.IntegerField(
        null=True,
        blank=True,
        help_text="from number of items",
    )
    to_number_of_items = models.IntegerField(
        null=True,
        blank=True,
        help_text="to number of items",
    )
    amount = models.IntegerField(default=1, help_text="You get")
    price = models.OneToOneField(
        Price,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        help_text="for the price of",
    )

    class Meta(OrderableModel.Meta):
        verbose_name = _("bulk price matrix item")
        verbose_name_plural = _("bulk price matrix items")


class Payment(
    PolymorphicModel,
    AdminLinkMixin,
    PublicKeyField,
    LogInfoFields,
):
    amount_paid = MoneyField(
        max_digits=15,
        decimal_places=2,
        default_currency="EUR",
        null=True,
    )
    confirmed_on = models.DateTimeField(null=True, blank=True)


class PaymentRequest(AdminLinkMixin, LogInfoFields):
    to_pay = models.OneToOneField(Price, on_delete=models.SET_NULL, null=True)


class PaymentRequestPayment(AdminLinkMixin, LogInfoFields):
    payment_request = models.ForeignKey(
        PaymentRequest,
        on_delete=models.CASCADE,
        null=True,
    )
    payment = models.ForeignKey(
        Payment,
        related_name="payments",
        on_delete=models.CASCADE,
        null=True,
    )
