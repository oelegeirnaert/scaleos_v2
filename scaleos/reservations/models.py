from django.db import models
from polymorphic.models import PolymorphicModel
from scaleos.shared.mixins import AdminLinkMixin, ITS_NOW
from scaleos.shared.fields import NameField
from django.utils.translation import gettext_lazy as _
import datetime

# Create your models here.

class Reservation(PolymorphicModel):
    person = models.ForeignKey(
        "hr.Person",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = _("reservation")
        verbose_name_plural = _("reservations")   

class BrunchReservation(Reservation):
    brunch = models.ForeignKey("events.BrunchEvent", related_name="reservations", on_delete=models.CASCADE, null=True, blank=False)