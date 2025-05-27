from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.stores.validators import validate_ean


class PurchasableItem(
    PolymorphicModel,
    AdminLinkMixin,
    NameField,
):
    class Meta:
        verbose_name = _("purchasable item")
        verbose_name_plural = _("purchasable items")


class Product(PurchasableItem):
    ean = models.CharField(
        max_length=13,
        unique=True,
        validators=[validate_ean],
        help_text=_("enter the 13-digit EAN code."),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")


class Service(PurchasableItem):
    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")


class Store(
    AdminLinkMixin,
    NameField,
    PublicKeyField,
):
    organization = models.ForeignKey(
        "organizations.Organization",
        verbose_name=_(
            "organization",
        ),
        related_name="shops",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )

    class Meta:
        verbose_name = _("store")
        verbose_name_plural = _("stores")
