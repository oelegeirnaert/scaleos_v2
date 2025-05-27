from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.models import CardModel


# Create your models here.
class Floor(PolymorphicModel, AdminLinkMixin, PublicKeyField, CardModel, models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        verbose_name=_("organization"),
        related_name="floors",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(verbose_name=_("name"), max_length=255)
    description = models.TextField(blank=True)
    level = models.IntegerField(verbose_name=_("level"), default=0)
    square_metres = models.IntegerField(
        verbose_name=_("square metres"),
        null=True,
        blank=True,
    )
    gps_surface = models.MultiPolygonField(null=True, blank=True)

    class Meta:
        verbose_name = _("floor")
        verbose_name_plural = _("floors")


class Building(Floor):
    class Meta:
        verbose_name = _("building")
        verbose_name_plural = _("buildings")


class Room(Floor):
    in_building = models.ForeignKey(
        Building,
        verbose_name=_("in building"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("room")
        verbose_name_plural = _("rooms")


class Terrace(Floor):
    class Meta:
        verbose_name = _("terrace")
        verbose_name_plural = _("terraces")
