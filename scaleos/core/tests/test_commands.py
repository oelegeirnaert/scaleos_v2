from django.core.management import call_command
from django.test import TestCase


class CommandsTestCase(TestCase):
    def test_create_html_templates_command(self):
        "Test my create html files command."

        args = []
        opts = {}
        call_command("create_html_templates", *args, **opts)
