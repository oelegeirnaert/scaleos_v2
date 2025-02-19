import logging
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create all the HTML files"

    def handle(self, *args, **options):  # noqa: C901
        self.stdout.write(self.style.SUCCESS("Okay, we will do so"))

        def create_template(template_name, template_location):  # pragma: no cover
            template_content = get_content(template_name)
            if template_content is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"\tWe do not have content for a {template_name} template",
                    ),
                )
                return

            full_template_location = f"{basepath}/{template_location}"
            output_file = Path(full_template_location)
            output_file.parent.mkdir(exist_ok=True, parents=True)
            output_file.write_text(template_content)
            self.stdout.write(self.style.SUCCESS(f"\tCreated {template_location}"))

        def get_content(the_template):  # pragma: no cover
            if the_template.lower() == "card_template":
                return """{# generated via manage create_html_scripts #}
{% extends 'card.html' %}
{% load i18n %}
        """

            if the_template.lower() == "page_template":
                return """{# generated via manage create_html_scripts #}
{% extends 'page.html' %}
{% load i18n %}
"""

            if the_template.lower() == "action_menu":
                return """{# generated via manage create_html_scripts #}
{% extends 'action_menu.html' %}
{% load i18n %}
"""

            if the_template.lower() == "detail_template":
                return """{# generated via manage create_html_scripts #}
{% extends 'detail.html' %}
{% load i18n %}
"""

            if the_template.lower() == "title_template":
                return """{# generated via manage create_html_scripts #}
{% extends 'title.html' %}
{% load i18n %}
"""
            return ""

        basepath = settings.TEMPLATES[0]["DIRS"][0]
        templates_to_generate = [
            "card_template",
            "action_menu",
            "page_template",
            "detail_template",
            "title_template",
        ]
        for app_label in settings.LOCAL_APPS:
            full_app_label = app_label.replace("scaleos.", "")
            self.stdout.write(self.style.SUCCESS(f"\n** Checking {full_app_label} **"))
            app_config = apps.get_app_config(full_app_label)
            models = app_config.models

            for a_model in models:
                the_model = apps.get_model(full_app_label, a_model)()
                for a_template_name in templates_to_generate:
                    if hasattr(the_model, a_template_name):
                        template_location = getattr(the_model, a_template_name)
                        try:
                            get_template(template_location)
                        except TemplateDoesNotExist as e:  # pragma: no cover
                            logger.info("Template does not exist: %s, so create it", e)
                            create_template(a_template_name, template_location)

        self.stdout.write(
            self.style.SUCCESS("Ready, now execute the following command"),
        )
        self.stdout.write(self.style.SUCCESS("sudo chmod 777 -R scaleos/templates"))
