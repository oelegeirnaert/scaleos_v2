import logging
from django.db import models
from djmoney.models.fields import MoneyField
from polymorphic.models import PolymorphicModel
from scaleos.shared.mixins import AdminLinkMixin, ITS_NOW
from scaleos.shared.fields import LogInfoFields
from moneyed import CURRENCIES
from moneyed import Money

logger = logging.getLogger(__name__)

# Create your models here.
class Price(LogInfoFields, AdminLinkMixin):
    current_price = MoneyField(
        max_digits=15,
        decimal_places=2,
        default_currency="EUR",
        null=True,
        blank=True,
    )

    includes_vat = models.BooleanField(default=True)
    vat_percentage = models.IntegerField(default=21)

    def __str__(self):
        return f"{self.current_price}"

    @property
    def price_text(self):
        if self.current_price == Money(0.00, "EUR"):
            return _("free")
        return f"{self.current_price}"

    @property
    def previous_price(self):
        if self.pk is None:
            logger.debug("save first")
            return None

        try:
            return self.price_history.all()[1].old_price
        except Exception:
            logger.exception("cannot get a previous price")

        return "no previous price."

    @property
    def price(self):
        return self.current_price

    @property
    def price_vat_excluded(self):
        try:
            return self.current_price - self.current_price * (self.vat_percentage / 100)
        except Exception:
            msg = "Cannot get the VAT excluded price"
            logger.exception(msg)
            return self.current_price

    @property
    def price_vat_included(self):
        if self.includes_vat:
            return self.current_price

        return self.current_price + self.current_price * (self.vat_percentage / 100)

    def save(self, *args, **kwargs):
        if self.pk is None:
            msg = _("save first")
            logger.debug(msg)
        if self.current_price != self.previous_price:
            msg = "The price changed"
            (
                new_price_history,
                new_price_history_created,
            ) = PriceHistory.objects.get_or_create(
                created_on=self.modified_on,
                old_price=self.current_price,
                price_id=self.id,
            )
            if new_price_history_created:
                logger.debug("New price history created.")
            logger.debug(msg)

        super().save(*args, **kwargs)


class PriceHistory(LogInfoFields):
    price = models.ForeignKey(
        Price,
        related_name="price_history",
        on_delete=models.SET_NULL,
        null=True,
    )
    old_price = MoneyField(
        max_digits=15,
        decimal_places=2,
        default_currency="EUR",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_on"]