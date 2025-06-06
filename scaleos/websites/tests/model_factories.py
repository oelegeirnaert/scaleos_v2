from factory import SubFactory
from factory.django import DjangoModelFactory

from scaleos.files.tests.model_factories import ImageFileFactory
from scaleos.organizations.tests.model_factories import OrganizationFactory
from scaleos.websites import models as website_models


class WebsiteFactory(DjangoModelFactory[website_models.Website]):
    class Meta:
        model = website_models.Website

    organization = SubFactory(OrganizationFactory)


class PageFactory(DjangoModelFactory[website_models.Page]):
    class Meta:
        model = website_models.Page

    website = SubFactory(WebsiteFactory)


class BlockFactory(DjangoModelFactory[website_models.Block]):
    class Meta:
        model = website_models.Block


class PageBlockFactory(DjangoModelFactory[website_models.PageBlock]):
    class Meta:
        model = website_models.PageBlock

    page = SubFactory(PageFactory)
    block = SubFactory(BlockFactory)


class ConceptsBlockFactory(DjangoModelFactory[website_models.ConceptsBlock]):
    class Meta:
        model = website_models.ConceptsBlock


class EventsBlockFactory(DjangoModelFactory[website_models.EventsBlock]):
    class Meta:
        model = website_models.EventsBlock


class ImageAndTextBlockFactory(
    DjangoModelFactory[website_models.ImageAndTextBlock],
):
    class Meta:
        model = website_models.ImageAndTextBlock


class CallToActionFactory(DjangoModelFactory[website_models.CallToAction]):
    class Meta:
        model = website_models.CallToAction

    website = SubFactory(WebsiteFactory)


class CTAVisitPageFactory(DjangoModelFactory[website_models.CTAVisitPage]):
    class Meta:
        model = website_models.CTAVisitPage

    page = SubFactory(PageFactory)


class CTAVisitExternalURLFactory(
    DjangoModelFactory[website_models.CTAVisitExternalURL],
):
    class Meta:
        model = website_models.CTAVisitExternalURL


class CallToActionBlockItemFactory(
    DjangoModelFactory[website_models.CallToActionBlockItem],
):
    class Meta:
        model = website_models.CallToActionBlockItem

    block = SubFactory(BlockFactory)
    call_to_action = SubFactory(CallToActionFactory)


class WebsiteImageFactory(DjangoModelFactory[website_models.WebsiteImage]):
    class Meta:
        model = website_models.WebsiteImage

    website = SubFactory(WebsiteFactory)
    image = SubFactory(ImageFileFactory)

class WebsiteDomainFactory(DjangoModelFactory[website_models.WebsiteDomain]):
    class Meta:
        model = website_models.WebsiteDomain

    domain_name = "example.com"
    website = SubFactory(WebsiteFactory)