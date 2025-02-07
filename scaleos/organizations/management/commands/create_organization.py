import logging
from django.core.management.base import BaseCommand, CommandError
from scaleos.organizations import models as organization_models
import datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create an organization"

    def add_arguments(self, parser):
        parser.add_argument('organization_name', type=str)

    
    def handle(self, *args, **options):
        organization_name = options.get('organization_name', None)
        
        result = None
        if organization_name and hasattr(self, organization_name):
            the_organization = getattr(self, organization_name)
            result = the_organization()

        if result is None:
            self.stdout.write(
                self.style.ERROR(f'invalid organization')
            )

    def waerboom(self):
        logger.info("Create or update waerboom")
        waerboom, created = organization_models.Enterprise.objects.get_or_create(registered_country="BE", registration_id="0460822848")
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'{waerboom} created')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'updating {waerboom}')
            )

        waerboom.name = "BRUSSELS WAERBOOM EVENT"
        waerboom.save()
        return True