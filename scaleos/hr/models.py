from django.db import models
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.fields import NameField
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import date



# Create your models here.
class Person(
    AdminLinkMixin,
    NameField,
):
    family_name = models.CharField(null=True)
    user = models.OneToOneField(
        get_user_model(),
        related_name="person",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    national_number = models.CharField(null=True, blank=True)
    middle_name = models.CharField(null=True, blank=True)
    
    nationality = models.CharField(null=True, blank=True)
    gender = models.CharField(null=True, blank=True)
    country = CountryField(null=True, blank=True)

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

    def __str__(self):
        if self.name and self.family_name:
            return f'{self.name} {self.family_name}'
        return super().__str__()
    
    @property
    def age(self):
        self.get_age()

    def get_age(self, today=None):
        if today is None:
                today = date.today()
        if self.birthday:
            return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))