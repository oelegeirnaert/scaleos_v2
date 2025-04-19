import logging

from django.apps import apps
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models import ForeignKey
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class AutoCompleteAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.autocomplete_fields = [
            field.name
            for field in model._meta.get_fields()  # noqa: SLF001
            if isinstance(field, ForeignKey)
        ]
        self.search_fields = []


class LogInfoAdminMixin(admin.ModelAdmin):
    readonly_fields = ["created_by", "created_on", "modified_on"]
    ordering = ["-created_on"]


class LogInfoInlineAdminMixin(admin.TabularInline):
    readonly_fields = ["created_on", "modified_on", "created_by"]
    ordering = ["-created_on"]
    autocomplete_fields = ["created_by", "modified_by"]


class LogInfoStackedInlineAdminMixin(admin.StackedInline):
    readonly_fields = ["created_on", "modified_on", "created_by"]
    ordering = ["-created_on"]
    autocomplete_fields = ["created_by", "modified_by"]


def generic_relation_reverse_link(self, obj, on_attr):
    if obj is None:
        return None
    if on_attr is None:
        return None

    logger.debug("Trying to get a generic relation for %s on %s", obj, on_attr)
    if not hasattr(obj, on_attr):
        msg = f"{obj} has no {on_attr}"
        logger.debug(msg)
        return msg

    the_attr = getattr(obj, on_attr)
    logger.debug("The attr: %s", the_attr)

    if hasattr(obj, f"{on_attr}_content_type"):
        the_ct = getattr(obj, f"{on_attr}_content_type")
    else:
        the_ct = ContentType.objects.get_for_model(the_attr)
    logger.debug("The ct is %s", the_ct)

    if hasattr(obj, f"{on_attr}_object_id"):
        the_obj_id = getattr(obj, f"{on_attr}_object_id")
    else:
        the_obj_id = the_attr.id
    logger.debug("OBJ ID: %s", the_obj_id)

    if the_attr:
        app_label = the_ct.app_label
        model_name = the_ct.model
        model = apps.get_model(app_label, model_name)
        model_str = str(model.objects.get(id=the_obj_id))
        url = reverse(
            f"admin:{the_ct.app_label}_{the_ct.model}_change",
            args=[the_obj_id],
        )
        logger.debug("url: %s", url)
        return mark_safe(f'<a href="{url}">{model_str}</a>')  # noqa: S308
    return "-"


class OriginAdminMixin(admin.ModelAdmin):
    readonly_fields = ["origin_link"]

    @admin.display(
        description=_("origin link"),
    )
    def origin_link(self, obj):
        return generic_relation_reverse_link(self, obj, "origin")


class OriginInlineAdminMixin(admin.TabularInline):
    @admin.display(
        description=_("origin"),
    )
    def origin_link(self, obj):
        return generic_relation_reverse_link(self, obj, "origin")


class OriginStackedAdminMixin(admin.StackedInline):
    @admin.display(
        description=_("origin"),
    )
    def origin_link(self, obj):
        return generic_relation_reverse_link(self, obj, "origin")
