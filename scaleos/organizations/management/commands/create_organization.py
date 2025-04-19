import datetime
import logging
import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from moneyed import EUR
from moneyed import Money

from scaleos.buildings import models as building_models
from scaleos.events import models as event_models
from scaleos.hr import models as hr_models
from scaleos.organizations import models as organization_models
from scaleos.payments import models as payment_models
from scaleos.reservations import models as reservation_models
from scaleos.shared.mixins import ITS_NOW
from scaleos.users import models as user_models

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

    def add_card_image(self, image_name, image_path, card):
        if os.path.exists(image_path):  # noqa: PTH110
            with open(image_path, "rb") as img_file:  # noqa: PTH123
                django_file = File(img_file)
                card.card_image.save(image_name, django_file, save=True)

    def create_brunch_concept(self, organization):  # noqa: PLR0915
        logger.info("Creating brunch concept for organization %s", organization)

        brunch_payment_settings, created = (
            payment_models.EventReservationPaymentSettings.objects.get_or_create(
                public_key="3f9f7a92-9c84-4b16-91d8-6d3d4b2b7c52",
            )
        )
        brunch_payment_settings.organization_id = organization.pk
        brunch_payment_settings.save()

        brunch_payment_condition, created = (
            payment_models.EventReservationPaymentCondition.objects.get_or_create(
                event_reservation_payment_settings_id=brunch_payment_settings.pk,
                only_when_group_exceeds=30,
            )
        )

        brunch_reservation_settings, created = (
            reservation_models.EventReservationSettings.objects.get_or_create(
                organization_id=organization.pk,
            )
        )
        brunch_age_prices_matrix, created = (
            payment_models.AgePriceMatrix.objects.get_or_create(
                public_key="14a9b5ab-9560-4d9a-81cb-43892daaa66c",
            )
        )
        brunch_age_prices_matrix.name = "Gastronomisch buffet prijzen"
        brunch_age_prices_matrix.save()

        logger.info("Creating baby item")
        baby_price_item, created = (
            payment_models.AgePriceMatrixItem.objects.get_or_create(
                from_age=0,
                till_age=4,
                age_price_matrix_id=brunch_age_prices_matrix.pk,
            )
        )
        baby_price_item.maximum_persons = 10
        baby_price_item.save()

        logger.info("Creating children item")
        children_price_item, created = (
            payment_models.AgePriceMatrixItem.objects.get_or_create(
                from_age=5,
                till_age=12,
                age_price_matrix_id=brunch_age_prices_matrix.pk,
            )
        )
        children_price_item.maximum_persons = 10
        children_price_item.save()

        logger.info("Creating children price")
        children_price, created = payment_models.Price.objects.get_or_create(
            public_key="a7d8f7e4-f14e-4827-82f0-cb135b5b17bf",
        )
        children_price.input_price = Money(38, EUR)
        children_price.unique_origin = children_price_item
        children_price.organization_id = organization.pk
        children_price.save()

        logger.info("Creating adolescent item")
        adolescent_price_item, created = (
            payment_models.AgePriceMatrixItem.objects.get_or_create(
                from_age=13,
                till_age=16,
                age_price_matrix_id=brunch_age_prices_matrix.pk,
            )
        )
        adolescent_price_item.maximum_persons = 10
        adolescent_price_item.save()

        logger.info("Creating adolescent price")
        adolescent_price, created = payment_models.Price.objects.get_or_create(
            public_key="35d67aad-7b29-45a7-9792-828af48330a6",
        )
        adolescent_price.input_price = Money(87, EUR)
        adolescent_price.organization_id = organization.pk
        adolescent_price.unique_origin = adolescent_price_item
        adolescent_price.save()

        logger.info("Creating adult item")
        adult_price_item, created = (
            payment_models.AgePriceMatrixItem.objects.get_or_create(
                from_age=17,
                age_price_matrix_id=brunch_age_prices_matrix.pk,
            )
        )
        adult_price_item.maximum_persons = 30
        adult_price_item.save()

        logger.info("Creating adult price")
        adult_price, created = payment_models.Price.objects.get_or_create(
            public_key="1fd1ce26-6eef-4c32-ab0b-18cff9d07de8",
        )
        adult_price.unique_origin = adult_price_item
        adult_price.input_price = Money(97, EUR)
        adult_price.organization_id = organization.pk
        adult_price.save()

        brunch_concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="a98995c7-de5a-48d5-a4cb-559ee69a1768",
        )

        brunch_concept.event_reservation_payment_settings_id = (
            brunch_payment_settings.pk
        )
        brunch_concept.reservation_settings_id = brunch_reservation_settings.pk

        brunch_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "brunch.jpg",
        )
        self.add_card_image(
            image_name="brunch.jpg",
            image_path=brunch_image,
            card=brunch_concept,
        )
        brunch_concept.name_nl = "Gastronomisch buffet op zondag"
        brunch_concept.default_starting_time = datetime.time(12, 0)
        brunch_concept.default_ending_time = datetime.time(23, 0)
        brunch_concept.card_description_nl = """Het gastronomisch buffet is de uitgetekende gelegenheid om te genieten op gastronomisch niveau. Een diversiteit aan kwaliteitsvolle gerechten en mooi gepresenteerd. Dit is een unieke gelegenheid om in klein aantal ook een gastronomisch feest op hoog niveau te kunnen vieren."""  # noqa: E501
        brunch_concept.save()

        brunch_prices_matrix, created = (
            event_models.ConceptPriceMatrix.objects.get_or_create(
                concept_id=brunch_concept.pk,
                price_matrix_id=brunch_age_prices_matrix.pk,
            )
        )

        brunch_event, created = event_models.BrunchEvent.objects.get_or_create(
            public_key="66d91661-0183-469d-8836-c3e2d47644e9",
        )
        brunch_event.concept_id = brunch_concept.pk
        brunch_event.starting_at = datetime.datetime(
            year=2025,
            month=3,
            day=30,
            hour=12,
            minute=0,
            second=0,
            tzinfo=datetime.UTC,
        )
        brunch_event.ending_on = datetime.datetime(
            year=2025,
            month=3,
            day=30,
            hour=16,
            minute=0,
            second=0,
            tzinfo=datetime.UTC,
        )

        brunch_event.name_ml = f"Gastronomisch buffet {brunch_concept.name}"
        brunch_event.maximum_number_of_guests = 300
        brunch_event.save()

        from_date = datetime.datetime(year=2025, month=3, day=30)  # noqa: DTZ001
        to_date = datetime.datetime(year=2025, month=5, day=30)  # noqa: DTZ001
        brunch_duplicator, created = event_models.EventDuplicator.objects.get_or_create(
            event_id=brunch_event.pk,
            from_date=from_date,
            to_date=to_date,
        )
        brunch_duplicator.duplicate()

    def create_organization_dinner_and_dance(self, organization):
        dinner_and_dance_concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            name="Dinner & Dance",
        )
        dinner_and_dance_concept.card_description_nl = """Beleef een onvergetelijke avond vol smaak en sfeer bij Dance & Dine Events! Wij combineren heerlijk dineren met een sprankelende danservaring op exclusieve locaties. Geniet van culinaire hoogstandjes, live muziek en een dansvloer waar je de avond weg swingt. Perfect voor een romantisch uitje, een feest met vrienden of een speciale gelegenheid."""  # noqa: E501
        dinner_and_dance_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "dinner_and_dance.jpg",
        )
        self.add_card_image(
            image_name="dinner_and_dance.jpg",
            image_path=dinner_and_dance_image,
            card=dinner_and_dance_concept,
        )
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

    def create_waerboom_owners(self, organization):
        user_tamara, created = user_models.User.objects.get_or_create(
            email="tamara.coppens@waerboom.com",
        )
        person_tamara, created = hr_models.Person.objects.get_or_create(
            user_id=user_tamara.pk,
        )
        person_tamara.name = "Tamara"
        person_tamara.family_name = "Coppens"
        person_tamara.save()

        organization_models.OrganizationOwner.objects.get_or_create(
            organization_id=organization.pk,
            person_id=person_tamara.pk,
        )

        tamara_phone, created = hr_models.PersonTelephoneNumber.objects.get_or_create(
            person_id=person_tamara.pk,
            telephone_number="+32476422939",
            telephone_type=hr_models.PersonTelephoneNumber.Telephone_Type.MOBILE,
        )

    def create_seminar_concept(self, organization):
        logger.info("Creating seminar concept for organization %s", organization)
        seminar_concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="3a3e982e-67f2-439b-8ee8-0c8f5cb62189",
        )

        seminar_concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "seminar.jpg",
        )
        self.add_card_image(
            image_name="seminar.jpg",
            image_path=seminar_concept_image,
            card=seminar_concept,
        )
        seminar_concept.card_description_nl = """Een seminarie, meeting, expositie of congres organiseren op de rand van Brussel kan perfect in één van onze veelzijdige vergaderzalen. Dit kan vanaf 10 tot meer dan 1000 personen. De zalen van de Waerboom zorgen voor onbegrensde mogelijkheden. Wij zijn perfect afgestemd op uw noden als organisator en staan u bij in de organisatie van uw vergadering.

Ons hotel met 45 charmante kamers maakt het ook perfect mogelijk om residentiële seminaries te organiseren: ideaal voor een meerdaagse opleidingen en teambuildings."""  # noqa: E501

        seminar_concept.segment = event_models.Concept.SEGMENT.B2B
        seminar_concept.name_nl = "Seminaries bij Waerboom"
        seminar_concept.save()

    def create_wedding_concept(self, organization):
        logger.info("Creating wedding concept for organization %s", organization)
        wedding_concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="f7feb27b-f12b-4f28-95e2-0846c32ee08f",
        )
        wedding_concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "wedding.jpg",
        )
        self.add_card_image(
            image_name="seminar.jpg",
            image_path=wedding_concept_image,
            card=wedding_concept,
        )
        wedding_concept.card_description_nl = """Ging jouw partner recent voor jou op de knie en stappen jullie binnenkort in het huwelijksbootje? Allereerst: proficiat! Zijn jullie op zoek naar een feestbeleving verborgen in het groen, waar traditie en trends elkaar ontmoeten in een rustige en landelijke omgeving? Onze unieke locatie – te Groot-Bijgaarden, net buiten de bruisende hoofdstad Brussel – met uitzonderlijke zalen, hult je huwelijk ongetwijfeld in een intieme atmosfeer, waar fonkelende lichtjes boven jullie zweven en magie nooit ver weg is.

Wij jongleren met verfijnde culinaire verwennerij, een prachtig kader, een uitstekende service en de kracht om onvergetelijke feestjes te bouwen. Jullie kiezen de gelukkige genodigden en het feestmaal, wij verzorgen de rest van a tot z: van de zaal, signalisatie, parking en ingang tot de tafel voor de cadeautjes, het krukje om even te rusten en de perfecte timing door de maître om tijdig die langverwachte openingsdans in te zetten.

Gaat jullie hartje sneller kloppen en zien jullie een landelijke, sprankelende (en instaworthy ;)) bruiloft wel zitten? Laat jullie droombruiloft tot leven komen bij Waerboom. Pssst… we hebben alvast een bijzonder trouwcadeau voor jullie!"""  # noqa: E501, RUF001
        wedding_concept.segment = event_models.Concept.SEGMENT.B2C
        wedding_concept.name_nl = "Trouwen bij Waerboom"
        wedding_concept.save()

    def create_buildings(self, organization):
        logger.info("Creating waerboom building for organization %s", organization)
        waerboom_building, created = building_models.Building.objects.get_or_create(
            public_key="15730be5-ab50-45b7-ac26-a35a1aa8ce8a",
            organization_id=organization.pk,
        )
        waerboom_building.name = "Waerboom"
        waerboom_building.save()

        logger.info("Creating rooms in waerboom building %s", organization)

        room_bosch, created = building_models.Room.objects.get_or_create(
            public_key="b306dd21-7db8-4135-9fd7-408a0822d4b8",
            in_building_id=waerboom_building.pk,
        )
        room_bosch.organization_id = organization.pk
        room_bosch.name = "Zaal Bosch"
        room_bosch.save()

        bosch_terrace, created = building_models.Terrace.objects.get_or_create(
            public_key="89963220-dd93-4e87-ac16-5f063bf71b09",
        )

        bosch_terrace.organization_id = organization.pk
        bosch_terrace.name = "Terrace Bosch"
        bosch_terrace.save()

        room_breugel, created = building_models.Room.objects.get_or_create(
            public_key="d2480db7-eaba-4258-b770-0ec46ef3a727",
            in_building_id=waerboom_building.pk,
        )
        room_breugel.organization_id = organization.pk
        room_breugel.name = "Zaal Breugel"
        room_breugel.save()

        room_memling, created = building_models.Room.objects.get_or_create(
            public_key="4fbc511c-0af9-431c-9c4b-f6d14b8a9c2d",
            in_building_id=waerboom_building.pk,
        )
        room_memling.organization_id = organization.pk
        room_memling.name = "Zaal Memling"
        room_memling.save()

        room_permeke, created = building_models.Room.objects.get_or_create(
            public_key="8b8de3d0-ad98-4a7d-bab0-21d7bcb3b8f7",
            in_building_id=waerboom_building.pk,
        )
        room_permeke.organization_id = organization.pk
        room_permeke.name = "Zaal Permeke"
        room_permeke.save()

        room_rubens, created = building_models.Room.objects.get_or_create(
            public_key="d8f7b1e4-3bea-451c-b999-3f18f75a663e",
            in_building_id=waerboom_building.pk,
        )
        room_rubens.organization_id = organization.pk
        room_rubens.name = "Zaal Rubens"
        room_rubens.save()

        waerboomhof_building, created = building_models.Building.objects.get_or_create(
            public_key="924a3867-9c15-436a-9ea8-064bad22c548",
            organization_id=organization.pk,
        )
        waerboomhof_building.name = "Waerboomhof"
        waerboomhof_building.save()

    def create_styling(
        self,
        organization,
        picture_dir="waerboom",
        primary_color="#ffffff",
        secondary_color="#989482",
        text_color="#202020",
    ):
        logger.info("Creating styling for organization %s", organization)
        styling, created = (
            organization_models.OrganizationStyling.objects.get_or_create(
                organization_id=organization.pk,
            )
        )

        styling.primary_color = primary_color
        styling.secondary_color = secondary_color
        styling.text_color = text_color

        image_folder = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            picture_dir,
        )  # Full path to the image folder

        if os.path.exists(image_folder):  # noqa: PTH110
            image_files = [
                f
                for f in os.listdir(image_folder)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]

            if image_files:
                for image_name in image_files:
                    image_path = os.path.join(image_folder, image_name)  # noqa: PTH118

                    with open(image_path, "rb") as img_file:  # noqa: PTH123
                        django_file = File(img_file)
                        styling.fav_icon.save(image_name, django_file, save=True)

                self.stdout.write(self.style.SUCCESS(f"Uploaded: {image_name}"))
            else:
                self.stdout.write(
                    self.style.WARNING("No image files found in the folder."),
                )
            return

        self.stdout.write(self.style.ERROR(f"Directory not found: {image_folder}"))

        styling.save()

    def create_waerboom_payment_methods(self, organization):
        logger.info("Creating payment methods for organization %s", organization)

        cash_payment_method, created = (
            payment_models.CashPaymentMethod.objects.get_or_create(
                public_key="072b5b09-b74f-48b7-8922-287794e2955c",
            )
        )
        waerboom_cash_payment_method, created = (
            organization_models.OrganizationPaymentMethod.objects.get_or_create(
                organization_id=organization.pk,
                payment_method_id=cash_payment_method.pk,
            )
        )

        money_transfer_payment_method, created = (
            payment_models.EPCMoneyTransferPaymentMethod.objects.get_or_create(
                public_key="fc9f61d6-5f2c-49e4-b914-09b3d8da37d1",
            )
        )
        waerboom_money_transfer_payment_method, created = (
            organization_models.OrganizationPaymentMethod.objects.get_or_create(
                organization_id=organization.pk,
                payment_method_id=money_transfer_payment_method.pk,
            )
        )
        money_transfer_payment_method.iban = "BE63426220901108"
        money_transfer_payment_method.save()

    def waerboom(self):
        logger.info("Create or update Waerboom")
        waerboom, created = organization_models.Enterprise.objects.get_or_create(
            registered_country="BE",
            registration_id="0460822848",
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"{waerboom} created"))
        else:  # pragma: no cover
            self.stdout.write(self.style.WARNING(f"updating {waerboom}"))

        waerboom_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "waerboom_hotel.jpg",
        )
        self.add_card_image(
            image_name="dinner_and_dance.jpg",
            image_path=waerboom_image,
            card=waerboom,
        )
        waerboom.name = "BRUSSELS WAERBOOM EVENT"
        waerboom.slug = "waerboom"
        waerboom.published_on = ITS_NOW
        waerboom.save()

        self.create_buildings(waerboom)
        self.create_styling(waerboom)
        self.create_brunch_concept(waerboom)
        self.create_organization_dinner_and_dance(waerboom)
        self.create_seminar_concept(waerboom)
        self.create_wedding_concept(waerboom)
        self.create_waerboom_owners(waerboom)
        self.create_waerboom_payment_methods(waerboom)

        return True

    def scaleos(self):
        logger.info("Create or update ScaleOS")
        organization, created = organization_models.Enterprise.objects.get_or_create(
            registered_country="BE",
            registration_id="0770914131",
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"{organization} created"))
        else:  # pragma: no cover
            self.stdout.write(self.style.WARNING(f"updating {organization}"))

        organization.name = "ScaleOS"
        organization.slug = "scaleos"
        organization.save()

        return True

    def lane_consulting(self):
        logger.info("Create or update Lane Consulting")

        lane_c, created = organization_models.Enterprise.objects.get_or_create(
            registered_country="BE",
            registration_id="1001289725",
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"{lane_c} created"))
        else:  # pragma: no cover
            self.stdout.write(self.style.WARNING(f"updating {lane_c}"))

        lane_consulting_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "lane_consulting",
            "images",
            "lane_consulting.jpeg",
        )
        self.add_card_image(
            image_name="dinner_and_dance.jpg",
            image_path=lane_consulting_image,
            card=lane_c,
        )

        lane_c.name = "Lane Consulting"
        lane_c.slug = "lane-c"
        lane_c.published_on = ITS_NOW
        lane_c.save()

        self.create_styling(
            lane_c,
            picture_dir="lane_consulting",
            primary_color="#67747f",
            secondary_color="#d4ad9b",
        )

        return True
