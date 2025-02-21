import datetime
import logging

from django.core.management.base import BaseCommand
from moneyed import EUR
from moneyed import Money

from scaleos.events import models as event_models
from scaleos.organizations import models as organization_models
from scaleos.payments import models as payment_models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create an organization"

    def add_arguments(self, parser):
        parser.add_argument("organization_name", type=str)

    def handle(self, *args, **options):
        organization_name = options.get("organization_name")

        result = None
        if organization_name and hasattr(self, organization_name):
            the_organization = getattr(self, organization_name)
            result = the_organization()

        if result is None:
            self.stdout.write(self.style.ERROR("invalid organization"))

    def create_organisation_brunch(self, organisation):
        brunch_age_prices_matrix, created = (
            payment_models.AgePriceMatrix.objects.get_or_create(
                public_key="14a9b5ab-9560-4d9a-81cb-43892daaa66c",
            )
        )
        brunch_age_prices_matrix.name = "Gastronomisch buffet prijzen"
        brunch_age_prices_matrix.save()

        baby_price, created = payment_models.Price.objects.get_or_create(
            public_key="d28c6bdd-3013-46c8-9753-386745bf7c08",
        )
        baby_price.current_price = Money(0, EUR)
        baby_price.save()
        baby_price_item, created = (
            payment_models.AgePriceMatrixItem.objects.get_or_create(
                from_age=0,
                till_age=4,
                age_price_matrix_id=brunch_age_prices_matrix.pk,
                price_id=baby_price.pk,
            )
        )
        baby_price_item.maximum_persons = 10
        baby_price_item.save()

        children_price, created = payment_models.Price.objects.get_or_create(
            public_key="a7d8f7e4-f14e-4827-82f0-cb135b5b17bf",
        )
        children_price.current_price = Money(38, EUR)
        children_price.save()
        children_price_item, created = (
            payment_models.AgePriceMatrixItem.objects.get_or_create(
                from_age=5,
                till_age=12,
                age_price_matrix_id=brunch_age_prices_matrix.pk,
                price_id=children_price.pk,
            )
        )
        children_price_item.maximum_persons = 10
        children_price_item.save()

        adolescent_price, created = payment_models.Price.objects.get_or_create(
            public_key="35d67aad-7b29-45a7-9792-828af48330a6",
        )
        adolescent_price.current_price = Money(87, EUR)
        adolescent_price.save()
        adolescent_price_item, created = (
            payment_models.AgePriceMatrixItem.objects.get_or_create(
                from_age=13,
                till_age=16,
                age_price_matrix_id=brunch_age_prices_matrix.pk,
                price_id=adolescent_price.pk,
            )
        )
        adolescent_price_item.maximum_persons = 10
        adolescent_price_item.save()

        adult_price, created = payment_models.Price.objects.get_or_create(
            public_key="1fd1ce26-6eef-4c32-ab0b-18cff9d07de8",
        )
        adult_price.current_price = Money(97, EUR)
        adult_price.save()
        adult_price_item, created = (
            payment_models.AgePriceMatrixItem.objects.get_or_create(
                from_age=17,
                age_price_matrix_id=brunch_age_prices_matrix.pk,
                price_id=adult_price.pk,
            )
        )
        adult_price_item.maximum_persons = 30
        adult_price_item.save()

        brunch_concept, created = event_models.BrunchConcept.objects.get_or_create(
            organizer_id=organisation.pk,
            name="Gastronomisch buffet op zondag",
        )
        brunch_concept.default_starting_time = datetime.time(12, 0)
        brunch_concept.default_ending_time = datetime.time(23, 0)
        brunch_concept.card_description = """Het gastronomisch buffet is de uitgetekende gelegenheid om te genieten op gastronomisch niveau. Een diversiteit aan kwaliteitsvolle gerechten en mooi gepresenteerd. Dit is een unieke gelegenheid om in klein aantal ook een gastronomisch feest op hoog niveau te kunnen vieren."""  # noqa: E501
        brunch_concept.save()

        brunch_prices_matrix, created = (
            event_models.ConceptPriceMatrix.objects.get_or_create(
                concept_id=brunch_concept.pk,
                price_matrix_id=brunch_age_prices_matrix.pk,
            )
        )

        from_date = datetime.date(
            year=2025,
            month=datetime.datetime.now(tz=datetime.UTC).month,
            day=1,
        )
        to_date = datetime.date(
            year=2025,
            month=datetime.datetime.now(tz=datetime.UTC).month + 1,
            day=1,
        )
        weekday = 7
        brunch_concept.generate(from_date=from_date, to_date=to_date, weekday=weekday)

    def create_organisation_dinner_and_dance(self, organisation):
        dinner_and_dance_concept, created = (
            event_models.DinnerAndDanceConcept.objects.get_or_create(
                organizer_id=organisation.pk,
                name="Dinner & Dance",
            )
        )
        dinner_and_dance_concept.card_description = """Beleef een onvergetelijke avond vol smaak en sfeer bij Dance & Dine Events! Wij combineren heerlijk dineren met een sprankelende danservaring op exclusieve locaties. Geniet van culinaire hoogstandjes, live muziek en een dansvloer waar je de avond weg swingt. Perfect voor een romantisch uitje, een feest met vrienden of een speciale gelegenheid."""  # noqa: E501
        dinner_and_dance_concept.save()
        reception, reception_created = (
            event_models.ReceptionEvent.objects.get_or_create(
                concept_id=dinner_and_dance_concept.pk,
            )
        )
        reception.name = f"Reception {dinner_and_dance_concept.name}"
        reception.save()

        dinner, dinner_created = event_models.DinnerEvent.objects.get_or_create(
            concept_id=dinner_and_dance_concept.pk,
        )
        dinner.name = f"Dinner {dinner_and_dance_concept.name}"
        dinner.save()

        dance, dance_created = event_models.DanceEvent.objects.get_or_create(
            concept_id=dinner_and_dance_concept.pk,
        )
        dance.name = f"Dance {dinner_and_dance_concept.name}"
        dance.save()

    def waerboom(self):
        logger.info("Create or update waerboom")
        waerboom, created = organization_models.Enterprise.objects.get_or_create(
            registered_country="BE",
            registration_id="0460822848",
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"{waerboom} created"))
        else:  # pragma: no cover
            self.stdout.write(self.style.WARNING(f"updating {waerboom}"))

        waerboom.name = "BRUSSELS WAERBOOM EVENT"
        waerboom.slug = "waerboom"
        waerboom.save()

        self.create_organisation_brunch(waerboom)
        self.create_organisation_dinner_and_dance(waerboom)

        return True
