# scaleos/websites/models.py

import logging

from admin_ordering.models import OrderableModel
from colorfield.fields import ColorField
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from polymorphic.models import PolymorphicModel

from scaleos.events import models as event_models
from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.fields import SegmentField
from scaleos.shared.mixins import ITS_NOW
from scaleos.shared.mixins import AdminLinkMixin

logger = logging.getLogger("scaleos")


class PublishOnWebsiteFields(models.Model):
    publish_from = models.DateTimeField(null=True, blank=True, auto_created=True)
    publish_till = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class ButtonFields(models.Model):
    button_text = models.CharField(
        verbose_name=_("button text"),
        default="",
        max_length=255,
    )
    button_text_color = ColorField(format="hexa", null=True)
    button_color = ColorField(format="hexa", null=True)

    class Meta:
        abstract = True


class CallToAction(
    PolymorphicModel,
    AdminLinkMixin,
    NameField,
    PublishOnWebsiteFields,
    ButtonFields,
):
    website = models.ForeignKey(
        "websites.Website",
        verbose_name=_(
            "website",
        ),
        related_name="call_to_actions",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )

    class Meta:
        verbose_name = _("call to action")
        verbose_name_plural = _("call to actions")

    def __str__(self) -> str:
        return super().__str__()

    def save(self, *args, **kwargs):
        try:
            if self.button_text_color is None:
                if self.website.organization.styling.primary_button_text_color:
                    self.button_text_color = (
                        self.website.organization.styling.primary_button_text_color
                    )
        except AttributeError:
            pass

        try:
            if self.button_color is None:
                if self.website.organization.styling.primary_button_text_color:
                    self.button_color = (
                        self.website.organization.styling.primary_button_color
                    )
        except AttributeError:
            pass

        super().save(*args, **kwargs)

    @property
    def cta_link(self):
        return ""


class CTAVisitPage(CallToAction):
    page = models.ForeignKey(
        "websites.Page",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )

    class Meta:
        verbose_name = _("visit page")
        verbose_name_plural = _("visit pages")

    def __str__(self):
        return self.page.name

    @property
    def cta_link(self):
        return reverse(
            "websites:page",
            kwargs={
                "domain_name": self.website.domain_name,
                "page_slug": self.page.slug,
            },
        )


class CTAVisitExternalURL(CallToAction):
    url = models.URLField(
        verbose_name=_("url"),
        default="",
        blank=False,
    )

    class Meta:
        verbose_name = _("visit external url")
        verbose_name_plural = _("visit external urls")

    def __str__(self):
        return self.url


# Create your models here.
class Website(
    TimeStampedModel,
    AdminLinkMixin,
    PublicKeyField,
):
    organization = models.OneToOneField(
        "organizations.organization",
        verbose_name=_(
            "organization",
        ),
        related_name="website",
        on_delete=models.CASCADE,
        null=True,
    )
    domain_name = models.CharField(verbose_name=_("domain name"), max_length=255)
    slogan = models.CharField(verbose_name=_("slogan"), default="", blank=True)

    homepage = models.OneToOneField(
        "websites.Page",
        related_name="homepage",
        verbose_name=_("homepage"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    terms_and_conditions_page = models.OneToOneField(
        "websites.Page",
        related_name="terms_and_conditions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    ask_segment = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("website")
        verbose_name_plural = _("websites")

    @property
    def main_menu(self):
        return self.published_pages.filter(show_in_main_menu=True).order_by("ordering")

    @property
    def footer_menu(self):
        return self.published_pages.filter(show_in_footer_menu=True).order_by(
            "ordering",
        )

    @property
    def published_pages(self):
        return self.pages.filter(
            Q(publish_from__lte=ITS_NOW)
            & (Q(publish_till__isnull=True) | Q(publish_till__gte=ITS_NOW)),
        ).order_by("ordering")

    def __str__(self):
        if self.domain_name:
            return self.domain_name
        return super().__str__()


class WebsiteImage(
    AdminLinkMixin,
    NameField,
):
    website = models.ForeignKey(
        Website,
        verbose_name=_("website"),
        related_name="images",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    alt_text = models.CharField(verbose_name=_("alt text"), default="", max_length=255)
    image = models.ImageField(verbose_name=_("image"), upload_to="websites/images/")

    class Meta:
        verbose_name = _("website image")
        verbose_name_plural = _("website images")


class Page(
    PolymorphicModel,
    AdminLinkMixin,
    NameField,
    TimeStampedModel,
    OrderableModel,
    PublishOnWebsiteFields,
    SegmentField,
):
    website = models.ForeignKey(
        Website,
        related_name="pages",
        on_delete=models.CASCADE,
        null=True,
    )
    parent_page = models.ForeignKey(
        "self",
        related_name="child_pages",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    show_in_main_menu = models.BooleanField(default=True)
    show_in_footer_menu = models.BooleanField(default=True)
    show_name_on_website = models.BooleanField(default=True)
    menu_name = models.CharField(default="", blank=True)

    banner_image = models.ForeignKey(
        "files.ImageFile",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    banner_height = models.CharField(default="500px;", blank=True)
    banner_title = models.CharField(default="", blank=True)
    banner_slogan = models.CharField(default="", blank=True)

    class Meta(OrderableModel.Meta):
        verbose_name = _("page")
        verbose_name_plural = _("pages")

    def __str__(self) -> str:
        if self.website:
            return f"{self.website.domain_name.upper()}: {self.name}"
        return super().__str__()

    @property
    def slogan_text(self):
        if self.slogan:
            return self.slogan
        return self.website.slogan

    @property
    def menu_item_name(self):
        if self.menu_name:
            return self.menu_name
        return self.name

    @property
    def published_blocks(self):
        return self.blocks.filter(
            Q(block__publish_from__lte=ITS_NOW)
            & (
                Q(block__publish_till__isnull=True)
                | Q(block__publish_till__gte=ITS_NOW)
            ),
        ).order_by("ordering")


class Block(
    PolymorphicModel,
    TimeStampedModel,
    AdminLinkMixin,
    NameField,
    PublishOnWebsiteFields,
    PublicKeyField,
):
    show_name_on_website = models.BooleanField(default=True)
    parent_block = models.ForeignKey(
        "self",
        related_name="blocks",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    rotate = models.IntegerField(default=0)
    margin_top = models.CharField(
        default="30px",
        help_text=_("with unit (ex: px, rem, em)"),
    )
    background_color = ColorField(format="hexa", default="#00000000", null=True)
    website = models.ForeignKey(
        Website,
        related_name="blocks",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = _("block")
        verbose_name_plural = _("blocks")

    def __str__(self) -> str:
        return super().__str__()


class ConceptsBlock(Block):
    class ConceptFilter(models.TextChoices):
        ALL = "ALL", _("show all")
        B2B = "B2B", _("show only b2b")
        B2C = "B2C", _("show only b2c")

    filter = models.CharField(
        max_length=50,
        choices=ConceptFilter.choices,
        default=ConceptFilter.ALL,
    )

    class Meta:
        verbose_name = _("concept block")
        verbose_name_plural = _("concepts blocks")

    def __str__(self) -> str:
        return super().__str__()

    @property
    def concepts(self):
        logger.debug("Getting all concepts")
        additional_filter = Q()
        match self.filter:
            case self.ConceptFilter.B2B:
                additional_filter = Q(segment=event_models.Concept.SegmentType.B2B)
            case self.ConceptFilter.B2C:
                additional_filter = Q(segment=event_models.Concept.SegmentType.B2C)

        organization = self.website.organization
        result = event_models.Concept.objects.filter(
            Q(organizer_id=organization.pk)
            & (Q(segment=event_models.Concept.SegmentType.BOTH) | additional_filter),
        )
        logger.debug("Results found: %s", result.count())
        return result


class EventsBlock(Block):
    class Meta:
        verbose_name = _("events block")
        verbose_name_plural = _("events blocks")

    def __str__(self) -> str:
        return super().__str__()

    @property
    def events(self):
        logger.setLevel(logging.DEBUG)
        logger.debug("Getting all events")
        organization = self.website.organization
        customer_concept_ids = event_models.CustomerConcept.objects.filter(
            organizer_id=organization.pk,
        ).values_list("id", flat=True)

        result = event_models.Event.objects.filter(
            concept__organizer_id=organization.pk,
        ).exclude(concept_id__in=customer_concept_ids)
        logger.debug("Results found: %s", result.count())
        return result


class ImageAndTextBlock(Block):
    class AlignType(models.TextChoices):
        LEFT = "LEFT", _("left")
        RIGHT = "RIGHT", _("right")

    image_alignment = models.CharField(
        max_length=5,
        choices=AlignType.choices,
        default=AlignType.LEFT,
    )
    text = models.TextField(default="", blank=True)
    image = models.ForeignKey(
        "files.ImageFile",
        related_name="image_and_text_blocks",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = _("image and text block")
        verbose_name_plural = _("image and text blocks")

    def __str__(self) -> str:
        return super().__str__()


class CallToActionBlockItem(AdminLinkMixin, OrderableModel):
    block = models.ForeignKey(
        Block,
        related_name="call_to_actions",
        on_delete=models.CASCADE,
        null=True,
    )
    call_to_action = models.ForeignKey(
        CallToAction,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta(OrderableModel.Meta):
        verbose_name = _("call to action block item")
        verbose_name_plural = _("call to action block items")


class PageBlock(AdminLinkMixin, OrderableModel):
    page = models.ForeignKey(
        Page,
        related_name="blocks",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    block = models.ForeignKey(Block, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return super().__str__()

    class Meta(OrderableModel.Meta):
        verbose_name = _("page block")
        verbose_name_plural = _("page blocks")
