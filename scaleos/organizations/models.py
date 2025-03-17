import logging

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.models import CardModel

logger = logging.getLogger(__name__)


# Create your models here.
class Organization(
    PolymorphicModel,
    AdminLinkMixin,
    NameField,
    CardModel,
    PublicKeyField,
):
    published_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")


class OrganizationOwner(AdminLinkMixin):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    person = models.ForeignKey(
        "hr.Person",
        related_name="owning_organizations",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )


class OrganizationCustomer(AdminLinkMixin, CardModel):
    organization = models.ForeignKey(
        Organization,
        related_name="customers",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    person = models.ForeignKey(
        "hr.Person",
        related_name="customer_at_organizations",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )


class Enterprise(Organization):
    registered_country = CountryField(null=True, default="BE")
    registration_id = models.CharField(default="", blank=True)
    gps_point = models.PointField(null=True, blank=True)

    class Meta:
        verbose_name = _("enterprise")
        verbose_name_plural = _("enterprises")
