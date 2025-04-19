import datetime
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from scaleos.shared.fields import LogInfoFields
from scaleos.shared.mixins import AdminLinkMixin

logger = logging.getLogger(__name__)


# Create your models here.
class Person(
    AdminLinkMixin,
):
    name = models.CharField(default="")
    family_name = models.CharField(default="")
    user = models.OneToOneField(
        get_user_model(),
        related_name="person",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    national_number = models.CharField(default="", blank=True)
    middle_name = models.CharField(default="", blank=True)

    nationality = models.CharField(default="", blank=True)

    """
    primary_address = models.ForeignKey(
        "geography.Location",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    """

    primary_mobile_number = PhoneNumberField(null=True, blank=True, unique=True)
    primary_email_address = models.EmailField(null=True, blank=True, unique=True)

    mother_tongue = models.CharField(
        max_length=50,
        choices=settings.LANGUAGES,
        default="",
        blank=True,
    )

    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        if self.name and self.family_name:
            return f"{self.name} {self.family_name}"
        return super().__str__()

    @property
    def age(self):
        return self.get_age()

    def get_age(self, today=None):
        if today is None:
            today = datetime.datetime.now(tz=datetime.UTC).date()

        if self.birthday:
            return (
                today.year
                - self.birthday.year
                - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
            )

        return None

    @property
    def primary_telephone_number(self):
        logger.debug("Trying to get the primary telephone number")

        logger.debug("Latest modified number is considered as being the primary number")
        telephone_num = self.telephone_numbers.order_by("-modified_on").first()
        if telephone_num and telephone_num.telephone_number:
            return telephone_num.telephone_number
        return None


class PersonAddress(AdminLinkMixin):
    person = models.ForeignKey(
        Person,
        related_name="addresses",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    address = models.OneToOneField(
        "geography.Address",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )


class PersonLanguage(AdminLinkMixin, LogInfoFields):
    person = models.ForeignKey(
        Person,
        related_name="languages",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    language = models.CharField(
        verbose_name=_("Language"),
        max_length=50,
        choices=settings.LANGUAGES,
        default="",
        blank=True,
    )
    is_mother_tongue = models.BooleanField(default=False)
    writing_score = models.IntegerField(
        verbose_name=_("Writing Score"),
        null=True,
        blank=True,
    )
    reading_score = models.IntegerField(
        verbose_name=_("Reading Score"),
        null=True,
        blank=True,
    )
    speaking_score = models.IntegerField(
        verbose_name=_("Speaking Score"),
        null=True,
        blank=True,
    )
    understanding_score = models.IntegerField(
        verbose_name=_("understanding_score"),
        null=True,
        blank=True,
    )


class PersonTelephoneNumber(AdminLinkMixin, LogInfoFields):
    class TelephoneType(models.TextChoices):
        MOBILE = "MOBILE", _("mobile")
        HOME = "HOME", _("home")
        WORK = "WORK", _("work")

    person = models.ForeignKey(
        Person,
        related_name="telephone_numbers",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    telephone_number = PhoneNumberField(null=True, blank=True)
    telephone_type = models.CharField(
        verbose_name=_("Telephone Type"),
        max_length=50,
        choices=TelephoneType.choices,
        default="",
        blank=True,
    )
