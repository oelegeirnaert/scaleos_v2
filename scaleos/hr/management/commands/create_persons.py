import logging
from django.core.management.base import BaseCommand, CommandError
from scaleos.hr import models as organization_models
from scaleos.hr.tests import model_factories
from scaleos.events import models as event_models
import datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create some fake persons"

    def add_arguments(self, parser):
        parser.add_argument('how_much', type=int)

    
    def handle(self, *args, **options):
        how_much = options.get('how_much', None)
        
        if how_much:
            self.stdout.write(
                self.style.SUCCESS(f'Creating {how_much} persons')
            )
            model_factories.PersonFactory.create_batch(how_much)