import datetime
import logging
from uuid import uuid4

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

ITS_NOW = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())  # noqa: DTZ005


class AdminLinkMixin(models.Model):
    class Meta:
        abstract = True

    @cached_property
    def model_name(self):
        return self._meta.model_name

    @cached_property
    def verbose_name(self):
        return self._meta.verbose_name

    @cached_property
    def verbose_name_plural(self):
        return self._meta.verbose_name_plural

    @cached_property
    def app_label(self):
        return self._meta.app_label

    @cached_property
    def admin_edit_button(self):
        url = reverse(
            f"admin:{self.app_label}_{self.model_name}_change",
            args=[self.id],
        )
        return mark_safe(  # noqa: S308
            f"""
            <a class="mt-2 inline-block rounded-sm border border-gray-600
            bg-gray-600 px-12 py-3 text-sm font-medium text-white
            hover:bg-transparent hover:text-gray-600
            focus:ring-3 focus:outline-hidden"
            href="{url}"
            target="_blank">
            Edit {self.verbose_name}
            </a>
            """,
        )

    @cached_property
    def card_list_template(self):  # pragma: no cover
        msg = "Use: include 'card_list.html' "
        raise Exception(msg)  # noqa: TRY002
        return f"{self.app_label}/{self.model_name}/card_list.html"

    @cached_property
    def action_menu(self):
        return f"{self.app_label}/{self.model_name}/action_menu.html"

    @cached_property
    def page_template(self):
        return f"{self.app_label}/{self.model_name}/page.html"

    @cached_property
    def page_button(self):
        try:
            url = reverse(
                f"{self.app_label}:{self.model_name}",
                args=[self.public_key],
            )
            return mark_safe(  # noqa: S308
                f"""
                <a class="mt-2 inline-block rounded-sm border
                border-gray-600 bg-gray-600 px-12 py-3
                text-sm font-medium text-white
                hover:bg-transparent hover:text-gray-600
                focus:ring-3 focus:outline-hidden"
                href="{url}">
                open {self.verbose_name}
                </a>
                """,
            )
        except Exception as e:  # noqa: BLE001
            logger.info(e)

    @cached_property
    def title_template(self):
        return f"{self.app_label}/{self.model_name}/title.html"

    @cached_property
    def detail_template(self):
        return f"{self.app_label}/{self.model_name}/detail.html"

    @cached_property
    def html_id(self):
        return f"htmlID{str(uuid4()).replace('-', '')}"

    @classmethod
    def list_template(cls):
        return f"{cls._meta.app_label}/{cls._meta.model_name}/list.html"

    @classmethod
    def class_name(cls):
        return cls._meta.model_name

    @cached_property
    def icon(self):
        the_icon = "bi-patch-question"
        if hasattr(self, "ICON"):
            the_icon = self.ICON  # pragma: no cover
        return mark_safe(f'<i class="bi {the_icon}"></i>')  # noqa: S308
