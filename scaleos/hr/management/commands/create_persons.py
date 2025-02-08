import logging

from django.core.management.base import BaseCommand

from scaleos.hr.tests import model_factories

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create some fake persons"

    def add_arguments(self, parser):
        parser.add_argument("how_much", type=int)

    def handle(self, *args, **options):
        how_much = options.get("how_much")

        if how_much:
            self.stdout.write(self.style.SUCCESS(f"Creating {how_much} persons"))
            model_factories.PersonFactory.create_batch(how_much)
