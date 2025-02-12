import logging

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import NameField
from scaleos.shared.mixins import AdminLinkMixin

logger = logging.getLogger(__name__)


# Create your models here.
class Organization(PolymorphicModel, AdminLinkMixin, NameField):
    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")


class Enterprise(Organization):
    registered_country = CountryField(null=True, default="BE")
    registration_id = models.CharField(default="", blank=True)
    gps_point = models.PointField(null=True, blank=True)

    class Meta:
        verbose_name = _("enterprise")
        verbose_name_plural = _("enterprises")
