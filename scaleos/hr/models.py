from django.db import models
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.fields import NameField
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.utils.translation import gettext_lazy as _




# Create your models here.
class Person(
    AdminLinkMixin,
    NameField,
):
    user = models.OneToOneField(
        get_user_model(),
        related_name="person",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    national_number = models.CharField(null=True, blank=True)
    middle_name = models.CharField(null=True, blank=True)
    family_name = models.CharField(null=True)
    nationality = models.CharField(null=True, blank=True)
    gender = models.CharField(null=True, blank=True)
    country = CountryField()

    """
    primary_address = models.ForeignKey(
        "geography.Location",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    """

    primary_mobile_number = PhoneNumberField(null=True, blank=True, unique=True)
    primary_telephone_number = PhoneNumberField(null=True, blank=True)

    primary_email_address = models.EmailField(null=True, blank=True, unique=True)

    mother_tongue = models.CharField(
        max_length=50,
        choices=settings.LANGUAGES,
        null=True,
        blank=True,
    )

    birthday = models.DateField(null=True, blank=True)