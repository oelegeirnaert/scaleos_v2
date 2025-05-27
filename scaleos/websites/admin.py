from admin_ordering.admin import OrderableAdmin
from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.websites import models as website_models


class PageBlockInlineAdmin(admin.StackedInline):
    model = website_models.PageBlock
    extra = 0
    show_change_link = True


class CallToActionBlockItem(admin.StackedInline):
    model = website_models.CallToActionBlockItem
    extra = 0
    show_change_link = True


class CallToActionInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class CallToActionInlineAdmin(StackedPolymorphicInline.Child):
        model = website_models.CallToAction
        show_change_link = True

    class CTAVisitPageInlineAdmin(StackedPolymorphicInline.Child):
        model = website_models.CTAVisitPage
        show_change_link = True

    class CTAVisitExternalURLInlineAdmin(StackedPolymorphicInline.Child):
        model = website_models.CTAVisitExternalURL
        show_change_link = True

    model = website_models.CallToAction
    child_inlines = (
        CallToActionInlineAdmin,
        CTAVisitPageInlineAdmin,
        CTAVisitExternalURLInlineAdmin,
    )


class BlockInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class BlockInlineAdmin(StackedPolymorphicInline.Child):
        model = website_models.Block
        show_change_link = True

    class ConceptsBlockInlineAdmin(StackedPolymorphicInline.Child):
        model = website_models.ConceptsBlock
        show_change_link = True

    class EventsBlockInlineAdmin(StackedPolymorphicInline.Child):
        model = website_models.EventsBlock
        show_change_link = True

    class ImageAndTextBlockInlineAdmin(StackedPolymorphicInline.Child):
        model = website_models.ImageAndTextBlock
        show_change_link = True

    model = website_models.Block
    child_inlines = (
        BlockInlineAdmin,
        ConceptsBlockInlineAdmin,
        EventsBlockInlineAdmin,
        ImageAndTextBlockInlineAdmin,
    )


class PageInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class PageInlineAdmin(StackedPolymorphicInline.Child):
        model = website_models.Page
        show_change_link = True

    model = website_models.Page
    child_inlines = (PageInlineAdmin,)


@admin.register(website_models.Website)
class WebsiteAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    readonly_fields = ["public_key"]
    inlines = [PageInlineAdmin, BlockInlineAdmin, CallToActionInlineAdmin]


# Register your models here.
@admin.register(website_models.Page)
class PageAdmin(
    OrderableAdmin,
    PolymorphicInlineSupportMixin,
    PolymorphicParentModelAdmin,
):
    base_model = website_models.Page
    child_models = [
        website_models.Page,  # Delete once a submodel has been added.
    ]
    list_filter = [PolymorphicChildModelFilter, "website"]
    inlines = [PageBlockInlineAdmin]
    list_editable = ["ordering"]
    list_display = ["__str__", "ordering"]


# Register your models here.
@admin.register(website_models.Block)
class BlockAdmin(PolymorphicParentModelAdmin):
    base_model = website_models.Block
    child_models = [
        website_models.Block,
        website_models.ConceptsBlock,
        website_models.EventsBlock,
        website_models.ImageAndTextBlock,
    ]
    list_filter = [PolymorphicChildModelFilter]
    inlines = [CallToActionBlockItem]
    readonly_fields = ["public_key"]


@admin.register(website_models.ConceptsBlock)
class ConceptsBlockAdmin(
    BlockAdmin,
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
):
    base_model = website_models.Block  # Explicitly set here!
    # define custom features here


@admin.register(website_models.EventsBlock)
class EventsBlockAdmin(
    BlockAdmin,
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
):
    base_model = website_models.Block


@admin.register(website_models.ImageAndTextBlock)
class ImageAndTextBlockBlockAdmin(
    BlockAdmin,
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
):
    base_model = website_models.Block


@admin.register(website_models.WebsiteImage)
class WebsiteImageAdmin(admin.ModelAdmin):
    pass


@admin.register(website_models.CallToAction)
class CallToActionAdmin(PolymorphicParentModelAdmin):
    base_model = website_models.CallToAction
    child_models = [
        website_models.CallToAction,
        website_models.CTAVisitPage,
        website_models.CTAVisitExternalURL,
    ]
    list_filter = [PolymorphicChildModelFilter]


@admin.register(website_models.CTAVisitPage)
class CTAVisitPageAdmin(
    CallToActionAdmin,
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
):
    base_model = website_models.CallToAction  # Explicitly set here!
    # define custom features here


@admin.register(website_models.CTAVisitExternalURL)
class CTAVisitExternalURLAdmin(
    CallToActionAdmin,
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
):
    base_model = website_models.CallToAction
