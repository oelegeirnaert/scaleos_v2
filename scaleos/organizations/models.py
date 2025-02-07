from django.db import models
from polymorphic.models import PolymorphicModel
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.fields import NameField
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

# Create your models here.
class Organization(PolymorphicModel, AdminLinkMixin, NameField):

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")

class Enterprise(Organization):
    registered_country = CountryField(null=True, default="BE")
    registration_id = models.CharField(null=True, blank=True)

    class Meta:
        verbose_name = _("enterprise")
        verbose_name_plural = _("enterprises")