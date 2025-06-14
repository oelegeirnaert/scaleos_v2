import logging

from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.gis.db import models
from django.db.models import Q
from django.forms import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from modeltranslation.translator import translator
from polymorphic.models import PolymorphicModel

from scaleos.hr.models import Person
from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import ITS_NOW
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.models import CardModel

logger = logging.getLogger(__name__)


class OrganizationField(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(class)s_list",
        null=True,
        blank=False,
    )

    class Meta:
        abstract = True


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
    primary_domain = models.OneToOneField(
        'websites.WebsiteDomain',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_for_organization'
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
        return OrganizationOwner.objects.filter(
            organization_id=self.pk,
            person_id=person_id,
        ).exists()


    def is_employee(self, user):
        if user.is_staff:
            return True

        if self.is_owner(user):
            return True

        if not hasattr(user, "person"):
            return False

        person_id = user.person.id
        return OrganizationEmployee.objects.filter(
            organization_id=self.pk,
            person_id=person_id,
        ).exists()



    def events_open_for_reservation(self):
        return self.events.filter(allow_reservations=True)

    @property
    def b2b_concepts(self):
        from scaleos.events.models import Concept

        return Concept.objects.filter(
            Q(organizer_id=self.pk)
            & (
                Q(segment=Concept.SegmentType.B2B) | Q(segment=Concept.SegmentType.BOTH)
            ),
        )

    @property
    def b2c_concepts(self):
        from scaleos.events.models import Concept

        return Concept.objects.filter(
            Q(organizer_id=self.pk)
            & (
                Q(segment=Concept.SegmentType.B2C) | Q(segment=Concept.SegmentType.BOTH)
            ),
        )

    @property
    def all_concepts(self):
        from scaleos.events.models import Concept

        return Concept.objects.filter(organizer_id=self.pk)

    @property
    def upcoming_public_events(self):
        from scaleos.events.models import SingleEvent

        return SingleEvent.objects.filter(
            starting_at__gte=ITS_NOW,
            concept__organizer_id=self.pk,
        )

    @property
    def upcoming_public_b2b_events(self):
        from scaleos.events.models import Concept

        return self.upcoming_public_events.filter(
            concept__segment=Concept.SegmentType.B2B,
        )

    @property
    def upcoming_public_b2c_events(self):
        from scaleos.events.models import Concept

        return self.upcoming_public_events.filter(
            concept__segment=Concept.SegmentType.B2C,
        )

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

        customer, created = B2CCustomer.objects.get_or_create(
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

    def get_event_types_with_count(self):
        return self.organizing_events.all()
    
    def clean(self):
        # Ensure primary_domain belongs to a website that belongs to this org
        if self.primary_domain:
            domain_org = self.primary_domain.website.organization
            if domain_org != self:
                raise ValidationError("Primary domain must belong to a website under this organization.")



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

class Customer(PolymorphicModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="customers",
    )

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")




class B2CCustomer(Customer):
    person = models.ForeignKey(
        "hr.Person",
        related_name="b2c_customers",
        verbose_name=_("person"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    def clean(self):
        if (
            B2CCustomer.objects.filter(
                person=self.person,
                organization=self.organization,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            msg = _("this person is already a customer from the organization")
            raise ValidationError(msg)
        return super().clean()

class B2BCustomer(Customer):
    b2b = models.ForeignKey(
        Organization,
        related_name="b2b_customers",
        on_delete=models.CASCADE,
        null=True,
    )

    def clean(self):
        if self.organization == self.b2b:
            raise ValidationError(_("you cannot add yourself as a customer"))
        return super().clean()

class Enterprise(Organization):
    registered_country = CountryField(null=True, default="BE")
    registration_id = models.CharField(default="", blank=True)
    gps_point = models.PointField(null=True, blank=True)

    class Meta:
        verbose_name = _("enterprise")
        verbose_name_plural = _("enterprises")

    @cached_property
    def vat_number(self):
        return f"{self.registered_country}{self.registration_id}"

    @property
    def headquarter(self):
        hq = self.addresses.first()
        if hq:
            return hq.address
        return None


class OrganizationAddress(AdminLinkMixin):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="addresses",
        null=True,
        blank=False,
    )
    address = models.ForeignKey(
        "geography.Address",
        verbose_name=_(
            "address",
        ),
        on_delete=models.SET_NULL,
        null=True,
    )


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
    primary_button_color = ColorField(default="#FFFFFF")
    primary_button_text_color = ColorField(default="#000000")



