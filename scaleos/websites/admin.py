from admin_ordering.admin import OrderableAdmin
from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from scaleos.websites import models as website_models

class WebsiteDomainInlineAdmin(admin.TabularInline):
    model = website_models.WebsiteDomain
    extra = 0
    readonly_fields = ["is_primary_display"]
    fields = ["domain_name", "is_primary_display"]

    def is_primary_display(self, obj):
        return obj.is_primary
    is_primary_display.short_description = "Primary?"
    is_primary_display.boolean = True

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
    readonly_fields = ["public_key", "url"]
    inlines = [WebsiteDomainInlineAdmin, PageInlineAdmin, BlockInlineAdmin, CallToActionInlineAdmin]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "primary_domain":
            # Get the object ID from the URL if editing an existing Website
            website_id = request.resolver_match.kwargs.get("object_id")
            if website_id:
                kwargs["queryset"] = website_models.WebsiteDomain.objects.filter(website_id=website_id)
            else:
                kwargs["queryset"] = website_models.WebsiteDomain.objects.none()  # prevent selection when adding
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
    readonly_fields = ["public_key"]


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

@admin.register(website_models.WebsiteDomain)
class WebsiteDomainAdmin(admin.ModelAdmin):
    list_display = ["__str__", "linked_website", "is_primary", "is_wildcard"]

    def linked_website(self, obj):
        if obj.website_id:
            url = reverse("admin:websites_website_change", args=[obj.website_id])
            return format_html('<a href="{}">{}</a>', url, obj.website)
        return "-"
    linked_website.short_description = _("website")
    linked_website.admin_order_field = "website"

