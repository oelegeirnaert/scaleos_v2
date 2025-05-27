import logging

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models import ForeignKey
from django.db.models import Model
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils.html import format_html
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


def build_generic_relation_link(  # noqa: PLR0913
    obj: Model,
    *,
    field_name: str,
    related_model: type[Model],
    related_model_admin: str | None = None,
    link_text: str | None = None,
    add_text: str | None = None,
) -> str:
    """
    Generate a link (HTML) to a generic related object or a button to add it.

    Parameters:
    - obj: the object with the GenericRelation
    - field_name: the name of the GenericRelation field on obj
    - related_model: the related model class
    - related_model_admin: optional 'app_modelname' string for reverse()
    - link_text: text for the edit link
    - add_text: text for the add button

    Returns:
    - Safe HTML string
    """
    if obj.pk is None:
        return _("add your %s after saving...") % field_name

    related_qs = getattr(obj, field_name).all()
    related = related_qs.first()

    model_name = related_model._meta.model_name  # noqa: SLF001
    app_label = related_model._meta.app_label  # noqa: SLF001
    admin_base = related_model_admin or f"{app_label}_{model_name}"

    if link_text is None:
        link_trans = _("edit")
        link_text = f"{link_trans} {related!s}"
    if add_text is None:
        text_trans = _("add")
        add_text = f"{text_trans} {model_name}"

    if related:
        url = reverse(f"admin:{admin_base}_change", args=[related.pk])
        return format_html('<a href="{}">{}</a>', url, link_text)
    content_type_id = ContentType.objects.get_for_model(obj).pk
    add_url = (
        reverse(f"admin:{admin_base}_add")
        + f"?content_type={content_type_id}&object_id={obj.pk}"
    )
    return format_html('<a class="button" href="{}">{}</a>', add_url, add_text)


def generic_fk_admin_link(content_object, content_type, object_id):
    """
    Returns a safe HTML link to the admin page of a GenericForeignKey object.
    """
    if content_object and content_type and object_id:
        try:
            url = reverse(
                f"admin:{content_type.app_label}_{content_type.model}_change",
                args=[object_id],
            )
            return format_html('<a href="{}">{}</a>', url, content_object)
        except NoReverseMatch:
            return str(content_object)  # fallback if reverse fails
    return "-"
