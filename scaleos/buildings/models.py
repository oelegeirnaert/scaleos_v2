from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.models import CardModel


# Create your models here.
class Floor(PolymorphicModel, AdminLinkMixin, PublicKeyField, CardModel, NameField):
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


class FloorLayout(NameField, AdminLinkMixin):
    floor = models.ForeignKey(
        Floor,
        verbose_name=_("floor"),
        related_name="layouts",
        on_delete=models.CASCADE,
        null=True,
    )


class Party(PolymorphicModel):
    def __str__(self):
        return super().__str__()


class Person(Party):
    linked_person = models.ForeignKey(
        "hr.Person",
        verbose_name=_("person"),
        on_delete=models.CASCADE,
        null=True,
    )


class Organization(Party):
    linked_organization = models.ForeignKey(
        "organizations.Organization",
        verbose_name=_("organization"),
        on_delete=models.CASCADE,
        null=True,
    )


class Building(NameField, AdminLinkMixin, CardModel, PublicKeyField):
    class Meta:
        verbose_name = _("building")
        verbose_name_plural = _("buildings")


class Room(Floor):
    building = models.ForeignKey(
        Building,
        verbose_name=_("building"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("room")
        verbose_name_plural = _("rooms")


class BathRoom(Room):
    class Meta:
        verbose_name = _("bath room")
        verbose_name_plural = _("bath rooms")


class HotelRoom(Room):
    class Meta:
        verbose_name = _("hotel room")
        verbose_name_plural = _("hotel rooms")


class LivingRoom(Room):
    class Meta:
        verbose_name = _("living room")
        verbose_name_plural = _("living rooms")


class Kitchen(Room):
    class Meta:
        verbose_name = _("kitchen")
        verbose_name_plural = _("kitchens")


class BedRoom(Room):
    class Meta:
        verbose_name = _("bedroom")
        verbose_name_plural = _("bedrooms")


class Office(Room):
    class Meta:
        verbose_name = _("office")
        verbose_name_plural = _("offices")


class Garage(Room):
    class Meta:
        verbose_name = _("garage")
        verbose_name_plural = _("garages")


class MeetingRoom(Room):
    class Meta:
        verbose_name = _("meeting room")
        verbose_name_plural = _("meeting rooms")


class LaundryRoom(Room):
    class Meta:
        verbose_name = _("laundry room")
        verbose_name_plural = _("laundry rooms")


class FitnessRoom(Room):
    class Meta:
        verbose_name = _("fitness room")
        verbose_name_plural = _("fitness rooms")


class SpaRoom(Room):
    class Meta:
        verbose_name = _("spa room")
        verbose_name_plural = _("spa rooms")


class SaunaRoom(Room):
    class Meta:
        verbose_name = _("sauna room")
        verbose_name_plural = _("sauna rooms")


class WC(Room):
    class Meta:
        verbose_name = _("WC")
        verbose_name_plural = _("WCs")


class Terrace(Floor):
    class Meta:
        verbose_name = _("terrace")
        verbose_name_plural = _("terraces")


class BuildingOwner(models.Model):
    building = models.ForeignKey(
        Building,
        related_name="owners",
        on_delete=models.CASCADE,
    )
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name="owning_buildings",
    )
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class BuildingTenant(models.Model):
    building = models.ForeignKey(
        Building,
        related_name="tenants",
        on_delete=models.CASCADE,
    )
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name="rented_buildings",
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class FloorOwner(models.Model):
    floor = models.ForeignKey(Floor, related_name="owners", on_delete=models.CASCADE)
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name="owning_floors",
    )
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class FloorTenant(models.Model):
    floor = models.ForeignKey(Floor, related_name="tenants", on_delete=models.CASCADE)
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name="rented_floors",
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
