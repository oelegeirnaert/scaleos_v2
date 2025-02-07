from django.core.management import call_command
from django.test import TestCase
from scaleos.organizations import models as organization_models

class CommandsTestCase(TestCase):
    def test_create_waerboom_management_command(self):
        " Test my custom command."

        args = ['waerboom']
        opts = {}
        call_command('create_organization', *args, **opts)
        assert organization_models.Enterprise.objects.get(registration_id="0460822848")

    def test_create_unknown_enterprise_management_command(self):
        " Test my custom command."

        args = ['unknown_enterprise']
        opts = {}
        call_command('create_organization', *args, **opts)
        assert organization_models.Organization.objects.count() == 0