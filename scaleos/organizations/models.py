import logging

from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.gis.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from modeltranslation.translator import translator
from polymorphic.models import PolymorphicModel

from scaleos.hr.models import Person
from scaleos.shared.fields import LogInfoFields
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
    network = models.OneToOneField(
        "hardware.Network",
        verbose_name=_(
            "network",
        ),
        related_name="organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    internal_url = models.URLField(
        null=True,
        blank=True,
        help_text="used for sending mails and notifications",
    )

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")

    def is_owner(self, user):
        if user.is_staff:
            return True

        if not hasattr(user, "person"):
            return False

        person_id = user.person.id
        return self.owners.filter(person_id=person_id).exists()

    def is_employee(self, user):
        if user.is_staff:
            return True

        if self.is_owner(user):
            return True

        if not hasattr(user, "person"):
            return False

        person_id = user.person.id
        return self.employees.filter(person_id=person_id).exists()

    def events_open_for_reservation(self):
        return self.events.filter(allow_reservations=True)

    def translate(self):  # noqa: C901
        try:
            ai_client = self.devices.first().services.first().client()
        except:  # noqa: E722
            return
        registered_models = translator.get_registered_models()
        for the_model in registered_models:
            the_fields = translator.get_options_for_model(the_model).fields
            instances = the_model.objects.all()
            for instance in instances:
                for lan in settings.LANGUAGES:
                    for field in the_fields:
                        the_text_to_translate = getattr(instance, f"{field}_{lan[0]}")
                        if len(the_text_to_translate.strip()) == 0:
                            continue

                        for lan2 in settings.LANGUAGES:
                            if lan2[0] == lan[0]:
                                continue

                            current_text = getattr(instance, f"{field}_{lan2[0]}")
                            if len(current_text.strip()) > 0:
                                logger.info("Already translated")
                                continue

                            to_language = lan2[1]
                            logger.info(
                                "Translate %s to %s",
                                the_text_to_translate,
                                to_language,
                            )
                            response = ai_client.chat(
                                model="mistral",
                                messages=[
                                    {
                                        "role": "system",
                                        "content": f"Translate the following text to {to_language} and I only need the translated text:",  # noqa: E501
                                    },
                                    {"role": "user", "content": the_text_to_translate},
                                ],
                            )
                            logger.info(response)
                            translated_text = response["message"]["content"]
                            logger.info(translated_text)
                            try:
                                setattr(instance, f"{field}_{lan2[0]}", translated_text)
                                instance.save()
                            except:  # noqa: E722
                                logger.info("we had an issue translating this")

    def add_b2c(self, user):
        logger.debug(
            "Adding a new B2C user from user %s to organization %s",
            user.pk,
            self.pk,
        )
        person, person_created = Person.objects.get_or_create(user_id=user.pk)
        if person_created:
            logger.info("New person (%s) created for user %s", person.pk, user.pk)

        customer, created = OrganizationCustomer.objects.get_or_create(
            organization=self,
            person_id=person.id,
        )
        if created:
            logger.info(
                "New customer (%s) created for organization %s",
                customer.pk,
                self.pk,
            )
        else:
            logger.debug("The customer already exists")

        return customer


class OrganizationMember(PolymorphicModel, AdminLinkMixin, LogInfoFields):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="members",
        null=True,
        blank=False,
    )
    person = models.ForeignKey(
        "hr.Person",
        related_name="memberships",
        verbose_name=_("person"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("organization member")
        verbose_name_plural = _("organization members")

    def __str__(self):
        if self.person and self.organization:
            return f"{self.person} - {self.organization}"
        if self.person:
            return f"{self.person}"
        return super().__str__()

    def clean(self):
        if not isinstance(self, B2BCustomer):
            msg = _("please choose your member")
            raise ValidationError({"person": msg})


class OrganizationOwner(OrganizationMember):
    class Meta:
        verbose_name = _("organization owner")
        verbose_name_plural = _("organization owners")

    def clean(self):
        if (
            OrganizationOwner.objects.filter(
                person=self.person,
                organization=self.organization,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            msg = _("this person is already owner from the organization")
            raise ValidationError(msg)
        return super().clean()


class OrganizationEmployee(OrganizationMember):
    class Meta:
        verbose_name = _("organization employee")
        verbose_name_plural = _("organization employees")

    def clean(self):
        if (
            OrganizationEmployee.objects.filter(
                person=self.person,
                organization=self.organization,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            msg = _("this person is already employee in the organization")
            raise ValidationError(msg)
        return super().clean()


class OrganizationCustomer(OrganizationMember):
    def clean(self):
        if (
            OrganizationCustomer.objects.filter(
                person=self.person,
                organization=self.organization,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            msg = _("this person is already a customer from the organization")
            raise ValidationError(msg)
        return super().clean()

    class Meta:
        verbose_name = _("organization customer")
        verbose_name_plural = _("organization customers")


class B2BCustomer(OrganizationCustomer):
    b2b = models.ForeignKey(
        Organization,
        related_name="suppliers",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )

    def clean(self):
        if self.organization == self.b2b:
            msg = _("you cannot add yourself as a customer")
            raise ValidationError({"b2b": msg})

        if (
            B2BCustomer.objects.filter(
                customer=self.customer,
                organization=self.organization,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            msg = _("this customer is already in the organization")
            raise ValidationError(msg)

        return super().clean()

    class Meta:
        verbose_name = _("b2b customer")
        verbose_name_plural = _("b2b customers")


class Enterprise(Organization):
    registered_country = CountryField(null=True, default="BE")
    registration_id = models.CharField(default="", blank=True)
    gps_point = models.PointField(null=True, blank=True)

    class Meta:
        verbose_name = _("enterprise")
        verbose_name_plural = _("enterprises")


class OrganizationStyling(AdminLinkMixin):
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name="styling",
        null=True,
        blank=False,
    )
    logo = models.ImageField(upload_to="organization/logos/", null=True, blank=True)
    fav_icon = models.ImageField(
        upload_to="organization/fav_icons/",
        null=True,
        blank=True,
    )
    primary_color = ColorField(default="#FFFFFF")
    secondary_color = ColorField(default="#FFFFFF")
    text_color = ColorField(default="#000000")


class OrganizationPaymentMethod(AdminLinkMixin, LogInfoFields):
    organization = models.ForeignKey(
        Organization,
        verbose_name=_(
            "organization",
        ),
        related_name="payment_methods",
        on_delete=models.SET_NULL,
        null=True,
    )
    payment_method = models.OneToOneField(
        "payments.PaymentMethod",
        verbose_name=_(
            "payment method",
        ),
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        if self.organization and self.payment_method:
            str_pay = _("pay")
            str_with = _("with")
            return f"{str_pay} {self.organization} {str_with} {self.payment_method.verbose_name}"  # noqa: E501
        return super().__str__()
