import datetime
import logging
import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from moneyed import EUR
from moneyed import Money

from scaleos.buildings import models as building_models
from scaleos.catering import models as catering_models
from scaleos.events import models as event_models
from scaleos.files import models as file_models
from scaleos.files.tasks import upload_files
from scaleos.geography import models as geography_models
from scaleos.hr import models as hr_models
from scaleos.organizations import models as organization_models
from scaleos.payments import models as payment_models
from scaleos.reservations import models as reservation_models
from scaleos.shared.mixins import ITS_NOW
from scaleos.users import models as user_models
from scaleos.websites import models as website_models

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
        children_price.vat_included = Money(38, EUR)
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
        adolescent_price.vat_included = Money(87, EUR)
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
        adult_price.vat_included = Money(97, EUR)
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
        brunch_concept.slogan = (
            "Zondags genieten bij de Waerboom – Gastronomisch buffet in stijl"  # noqa: RUF001
        )
        brunch_concept.name_nl = "Gastronomisch buffet op zondag"
        brunch_concept.default_starting_time = datetime.time(12, 0)
        brunch_concept.default_ending_time = datetime.time(23, 0)
        brunch_concept.card_description_nl = """Zin in een culinaire verwennerij om het weekend af te sluiten in schoonheid?
Elke zondag verwelkomt de Waerboom je met een uitgebreid gastronomisch buffet, waar kwaliteit, gezelligheid en verfijning centraal staan.

Laat je verrassen door een rijk aanbod aan smaakvolle gerechten – van verfijnde voorgerechten tot heerlijke warme creaties en een verleidelijk dessertenbuffet, allemaal met zorg en liefde bereid door onze chefs.

🍽️ Gastronomisch buffet met seizoensproducten
🥂 Aperitief en aangepaste wijnen mogelijk
👨‍👩‍👧‍👦 Gezellig tafelen met familie of vrienden
🏰 Stijlvolle setting en persoonlijke service

Of je nu iets te vieren hebt of gewoon wil genieten van een ontspannen zondag in een elegant kader – ons buffet staat garant voor een smakelijke en sfeervolle ervaring.

Zondag is buffetdag.
Reserveer je tafel en proef de verfijning van de Waerboom."""  # noqa: E501, RUF001
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

    def create_dinner_and_dance_concept(self, organization):
        dinner_and_dance_concept, created = event_models.Concept.objects.get_or_create(
            public_key="c1b647d8-646b-4797-8897-71e11937fed3",
        )

        dinner_and_dance_concept.organizer_id = organization.pk
        dinner_and_dance_concept.name = "Dinner & Dance"
        dinner_and_dance_concept.card_description_nl = """Zin in een stijlvolle avond waar culinaire verwennerij en dansplezier hand in hand gaan?
Ontdek ons Dinner & Dance-concept in de unieke setting van de Waerboom – dé locatie waar genieten, sfeer en beweging samenkomen.

Laat je verwennen met een verfijnd diner, geserveerd in een elegant kader, gevolgd door een bruisende dansavond met livemuziek of DJ. Ideaal voor een speciale gelegenheid, een bedrijfsfeest of gewoon… omdat je het leven wil vieren!

✨ Stijlvol viergangendiner of luxueus buffet
🎶 Dansvloer met livemuziek of DJ
🍸 Sfeervolle bar en lounge
💫 Perfecte setting voor een onvergetelijke avond

Of je nu met een select gezelschap komt of een groots event plant – wij zorgen voor de juiste toon en de perfecte service.

Dans, dineer en beleef.
Jouw avond begint bij de Waerboom."""  # noqa: E501, RUF001
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
        dinner_and_dance_concept.slogan = "Een avond vol klasse, smaak en ritme"
        dinner_and_dance_concept.save()

        event_mix, created = event_models.EventMix.objects.get_or_create(
            public_key="3f2e1c58-73b2-4d93-bf44-8ad7dbf34b99",
        )
        event_mix.concept_id = dinner_and_dance_concept.pk
        event_mix.name = "Dinner & Dance - Zomer Editie"
        event_mix.save()

        reception, reception_created = (
            event_models.ReceptionEvent.objects.get_or_create(
                concept_id=dinner_and_dance_concept.pk,
            )
        )
        reception.name = f"Reception {dinner_and_dance_concept.name}"
        reception.parent_id = event_mix.pk
        reception.save()

        dinner, dinner_created = event_models.DinnerEvent.objects.get_or_create(
            concept_id=dinner_and_dance_concept.pk,
        )
        dinner.name = f"Dinner {dinner_and_dance_concept.name}"
        dinner.parent_id = event_mix.pk
        dinner.save()

        dance, dance_created = event_models.DanceEvent.objects.get_or_create(
            concept_id=dinner_and_dance_concept.pk,
        )
        dance.parent_id = event_mix.pk
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

        hr_models.PersonTelephoneNumber.objects.get_or_create(
            person_id=person_tamara.pk,
            telephone_number="+32476422939",
            telephone_type=hr_models.PersonTelephoneNumber.TelephoneType.MOBILE,
        )

    def create_hoevefeesten_concept(self, organization):
        logger.info("Creating hoevefeesten concept for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="3a9d8072-f25a-4b0f-b1f3-159b1895a781",
        )

        hoevefeesten_concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "hoevefeesten.jpg",
        )
        self.add_card_image(
            image_name="hoevefeesten.jpg",
            image_path=hoevefeesten_concept_image,
            card=concept,
        )
        concept.card_description_nl = """Zodra de zon begint te schijnen, komt de traditie weer tot leven: de Hoevefeesten zijn terug!
Op onze sfeervolle binnenplaats vieren we de zomer zoals het hoort – met live bands, dj's, lekker eten en een geweldige sfeer.

Deze zwoele zondagen zijn al jaren een vaste waarde bij de Waerboom en trekken jong en oud voor een heerlijke mix van muziek, samenzijn en ambiance.

🎶 Live muziek en dj-sets in openlucht
🍔 Streetfood, barbecue en verfrissende drankjes
🪩 Dansen onder de sterrenhemel
🌞 Zomerse sfeer op een unieke hoevesite
👨‍👩‍👧‍👦 Gezellig voor het hele gezin

Of je nu komt om te dansen, te genieten van de muziek of gewoon om bij te praten met vrienden in een ontspannen setting – de Hoevefeesten staan garant voor zomerplezier zoals het moet zijn.

Beleef de zomer zoals alleen de Waerboom dat kan.
Mis deze iconische zondagen niet!"""  # noqa: E501, RUF001

        concept.segment = event_models.Concept.SegmentType.BOTH
        concept.name = "Hoevefeesten"
        concept.slogan = "De Hoevefeesten – Zomer, sfeer & muziek bij de Waerboom"  # noqa: RUF001
        concept.save()

        event_mix, created = event_models.EventMix.objects.get_or_create(
            public_key="9d2d0b1f-0f14-45f3-9cd9-91c3b845832e",
        )

        event_mix.concept_id = concept.pk
        event_mix.name = "Hoevefeesten 2025"
        event_mix.save()

        reception, created = event_models.ReceptionEvent.objects.get_or_create(
            public_key="f1e6a1b0-3a62-4560-9a9b-30a72a0c50bb",
        )
        if created:
            reception.starting_at = datetime.datetime(
                year=2025,
                month=8,
                day=24,
                hour=12,
                minute=0,
                second=0,
                tzinfo=datetime.UTC,
            )
            reception.ending_on = datetime.datetime(
                year=2025,
                month=8,
                day=24,
                hour=13,
                minute=0,
                second=0,
                tzinfo=datetime.UTC,
            )
        reception.name = "Receptie"
        reception.concept_id = concept.pk
        reception.parent_id = event_mix.pk
        reception.save()

        performance_1, created = (
            event_models.LivePerformanceEvent.objects.get_or_create(
                public_key="f6a2898c-481d-4d0a-9b5b-c62dbb913b77",
            )
        )

        if created:
            performance_1.starting_at = datetime.datetime(
                year=2025,
                month=8,
                day=24,
                hour=18,
                minute=0,
                second=0,
                tzinfo=datetime.UTC,
            )
            performance_1.ending_on = datetime.datetime(
                year=2025,
                month=8,
                day=24,
                hour=19,
                minute=0,
                second=0,
                tzinfo=datetime.UTC,
            )
        performance_1.concept_id = concept.pk
        performance_1.parent_id = event_mix.pk
        performance_1.name = "Abba 4 U"
        performance_1.save()

        performance_2, created = (
            event_models.LivePerformanceEvent.objects.get_or_create(
                public_key="4739c25c-7d3a-4606-a262-c958835eb828",
            )
        )

        if created:
            performance_2.starting_at = datetime.datetime(
                year=2025,
                month=8,
                day=24,
                hour=19,
                minute=0,
                second=0,
                tzinfo=datetime.UTC,
            )
            performance_2.ending_on = datetime.datetime(
                year=2025,
                month=8,
                day=24,
                hour=20,
                minute=0,
                second=0,
                tzinfo=datetime.UTC,
            )
        performance_2.concept_id = concept.pk
        performance_2.parent_id = event_mix.pk
        performance_2.name = "2Fabiola"
        performance_2.save()

        dinner, created = event_models.DinnerEvent.objects.get_or_create(
            public_key="3ba02138-c2a7-432c-9446-e1f958b7287d",
        )

        if created:
            dinner.starting_at = datetime.datetime(
                year=2025,
                month=8,
                day=24,
                hour=13,
                minute=0,
                second=0,
                tzinfo=datetime.UTC,
            )
            dinner.ending_on = datetime.datetime(
                year=2025,
                month=8,
                day=24,
                hour=17,
                minute=0,
                second=0,
                tzinfo=datetime.UTC,
            )
        dinner.concept_id = concept.pk
        dinner.parent_id = event_mix.pk
        dinner.name = "Luxery Dinner"
        dinner.save()

    def create_employee_party(self, organization):
        logger.info("Creating employee party concept for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="3c6ef9d4-7c69-4a49-8c98-9a28d6573e1f",
        )

        seminar_concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "employee_party.jpg",
        )
        self.add_card_image(
            image_name="employee_party.jpg",
            image_path=seminar_concept_image,
            card=concept,
        )
        concept.card_description_nl = """Een sterk team verdient een warm en onvergetelijk moment.
Bij de Waerboom maken we van jouw personeelsfeest een feestelijke totaalbeleving. Of je nu kiest voor een sprankelende receptie, een verfijnd diner of een knallende dansavond – wij zorgen voor de juiste sfeer, uitstekende service en culinaire verwennerij.

🎉 Zalen voor elk formaat, van intiem tot groots
🍽️ Buffetten, walking dinners of à la carte formules
🎵 DJ, liveband of eigen entertainment mogelijk
🛏️ Overnachtingsoptie voor wie wil blijven
🅿️ Grote gratis parking en vlotte bereikbaarheid

We denken met je mee over het concept, de aankleding en het verloop, zodat jij vol vertrouwen kunt uitkijken naar een avond waarop collega’s écht kunnen genieten.

Vier inzet, verbondenheid en successen – samen bij de Waerboom."""  # noqa: E501, RUF001
        concept.slogan = "Personeelsfeesten bij de Waerboom – Bedank je team in stijl"  # noqa: RUF001
        concept.segment = event_models.Concept.SegmentType.B2B
        concept.name_nl = "Personeelsfeesten"
        concept.save()

    def create_meeting_concept(self, organization):
        logger.info("Creating meeting concept for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="7e8b2cae-f9c7-47c2-b13b-4bd2d7b5c9a7",
        )

        seminar_concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "meeting.jpg",
        )
        self.add_card_image(
            image_name="meeting.jpg",
            image_path=seminar_concept_image,
            card=concept,
        )
        concept.card_description_nl = """Soms maakt de omgeving het verschil.
Bij de Waerboom vergader je in alle rust en comfort, ver weg van de dagelijkse drukte – maar met alles binnen handbereik. Of het nu gaat om een korte brainstorm, een strategische dagmeeting of een meerdaags overleg: wij zorgen voor een vlotte en professionele omkadering.

🗂️ Zalen in alle formaten, met daglicht en moderne technologie
📡 Snelle wifi, beamer, flipcharts en audiovisuele ondersteuning
🥐 Formules met koffie, ontbijt, lunch of uitgebreid diner
🅿️ Ruime gratis parking en centrale ligging

Onze ervaren eventcoördinatie staat klaar om alles tot in de puntjes te regelen, zodat jij en je team zich kunnen focussen op wat écht telt.

Professioneel vergaderen in een omgeving die inspireert – welkom bij de Waerboom.

<b>Meerdaagse Meeting</b>

Soms vraagt een goed overleg net iets meer tijd en ruimte.
Voor meerdaagse vergaderingen biedt de Waerboom een totaalpakket waarbij je in alle rust kunt werken, dineren en overnachten op één stijlvolle locatie.

🛏️ Comfortabele hotelkamers op de site
🍽️ Verzorgde maaltijden van ontbijt tot avondservice
🗂️ Vergaderzalen met alle technische voorzieningen
🌳 Groene omgeving voor wandelbreaks of informele momenten

Zo creëer je niet alleen efficiëntie, maar ook verbinding – met de juiste balans tussen inspanning en ontspanning.

Alles onder één dak voor een vergadering die blijft hangen.

<b>Internationale Meeting</b>

Ontvang je internationale gasten of organiseer je een bijeenkomst met deelnemers uit het buitenland?
De Waerboom biedt een professionele en gastvrije omgeving waar taal, cultuur en comfort hand in hand gaan.

🌍 Meertalige ondersteuning en op maat gemaakte ontvangst
🛬 Vlotte bereikbaarheid vanaf Brussels Airport
🏨 Verblijfsmogelijkheid ter plaatse
🍷 Gastronomische catering met Belgische flair

Of het nu gaat om een internationale boardmeeting, training of presentatie – bij ons voelen je gasten zich meteen welkom én professioneel omkaderd.

Versterk je internationale uitstraling, van ontvangst tot overnachting.
"""  # noqa: E501, RUF001
        concept.slogan = (
            "Vergaderen bij de Waerboom – Efficiënt, stijlvol en volledig verzorgd"  # noqa: RUF001
        )
        concept.segment = event_models.Concept.SegmentType.B2B
        concept.name_nl = "Meetings"
        concept.save()

    def create_business_lunch(self, organization):
        logger.info("Creating business lunch concept for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="2f8b8e44-7e56-4b8f-9c68-4302c06a2e7c",
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
            image_name="business_lunch.jpg",
            image_path=seminar_concept_image,
            card=concept,
        )
        concept.card_description_nl = """Geniet van verfijnde gerechten in een inspirerende omgeving waar ondernemers, professionals en beslissingsnemers samenkomen om ideeën te delen en nieuwe connecties te leggen. Onze business lunches combineren culinaire klasse met doeltreffend zakendoen, ideaal om relaties te verdiepen of nieuwe opportuniteiten te ontdekken.

👉 Reserveer uw tafel vandaag
👉 Netwerk in stijl, lunch met impact
👉 Ervaar de professionele gastvrijheid van de Waerboom"""  # noqa: E501, RUF001
        concept.slogan = (
            "Versterk uw netwerk tijdens een stijlvolle Business Lunch bij de Waerboom"
        )
        concept.segment = event_models.Concept.SegmentType.B2B
        concept.name_nl = "Business Lunch"
        concept.save()

    def create_business_breakfast_club_concept(self, organization):
        logger.info(
            "Creating business breakfast club concept for organization %s",
            organization,
        )
        concept, created = event_models.Concept.objects.get_or_create(
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
            card=concept,
        )
        concept.card_description_nl = """De kracht van een goed idee? Het begint vaak bij een goed gesprek.
Bij de Business Breakfast Club van de Waerboom brengen we ondernemers, beslissingsnemers en professionals samen voor een stijlvol ontbijt vol inspiratie, inzichten en waardevolle ontmoetingen.

In een warme, professionele setting geniet je van een verzorgd ontbijtbuffet terwijl een gastspreker je prikkelt met een kort maar krachtig verhaal. Daarna is er ruimte voor netwerking en verdiepende gesprekken.

☕ Heerlijke ontbijtformules met verse producten
🎤 Gastsprekers met visie uit verschillende sectoren
🤝 Gericht netwerken met gelijkgestemde professionals
🏛️ Stijlvolle locatie met vlotte bereikbaarheid en parking

Of je nu komt om ideeën te delen, nieuwe samenwerkingen te verkennen of gewoon de dag sterk te beginnen – bij de Business Breakfast Club start je altijd met voorsprong.

Begin je dag slim. Ontmoet, leer, verbind. Bij de Waerboom."""  # noqa: E501, RUF001
        concept.slogan = "Business Breakfast Club bij de Waerboom – Start de dag met inspiratie en connectie"  # noqa: E501, RUF001
        concept.segment = event_models.Concept.SegmentType.B2B
        concept.name_nl = "Business Breakfast Club"
        concept.save()

    def create_seminar_concept(self, organization):
        logger.info("Creating seminar concept for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
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
            card=concept,
        )
        concept.card_description_nl = """Op zoek naar een inspirerende locatie voor uw volgende bedrijfsseminarie?
Bij de Waerboom combineren we professionele faciliteiten met een stijlvolle omgeving, zodat u en uw team zich volledig kunnen focussen op wat echt telt: inhoud, interactie en resultaat.

Met moderne vergaderruimtes, high-end technologie, flexibele formules en een verfijnde catering, zorgen wij voor een perfect georganiseerde dag – van ontvangst tot afsluitende netwerkmomenten.

📊 Zalen op maat – van kleine vergaderingen tot grote conferenties
🔈 Professionele audiovisuele ondersteuning en wifi
🍴 Koffiepauzes, lunch, walking dinner of gastronomisch diner
🛏️ Overnachtingsmogelijkheden op de site
🅿️ Ruime gratis parking

Of het nu gaat om een teamdag, productpresentatie, opleiding of meerdaags congres – bij de Waerboom bent u zeker van een vlot verloop en een verzorgde totaalbeleving.

Professioneel, efficiënt én gastvrij.
Kies voor een seminarie met impact – kies voor de Waerboom."""  # noqa: E501, RUF001
        concept.slogan = "Succesvolle seminaries in stijl – bij de Waerboom"  # noqa: RUF001
        concept.segment = event_models.Concept.SegmentType.B2B
        concept.name_nl = "Seminaries"
        concept.save()

    def create_product_launch_concept(self, organization):
        logger.info("Creating product launch concept for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="6a14e62a-cd4f-4eec-8d28-705b14524737",
        )

        seminar_concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "product_launch.jpg",
        )
        self.add_card_image(
            image_name="product_launch.jpg",
            image_path=seminar_concept_image,
            card=concept,
        )
        concept.card_description_nl = """Een nieuw product verdient een krachtige eerste indruk.
Bij de Waerboom creëren we de perfecte setting voor een onvergetelijke productlancering, waar sfeer, techniek en presentatie naadloos samenkomen.

Of het nu gaat om een innovatief technisch product, een luxueus lifestylemerk of een nieuwe dienst – wij zorgen voor een professionele omkadering die indruk maakt op uw gasten én versterkt wat u wil uitstralen.

🚀 Stijlvolle en moduleerbare ruimtes voor elk concept
🎤 Audiovisuele ondersteuning met licht, geluid en projectie
✨ Sterke scenografie en brandingmogelijkheden
🍸 Verfijnde catering en receptieformules
🛏️ Overnachtingsmogelijkheden op locatie
🅿️ Grote gratis parking en vlotte bereikbaarheid

Van intieme persmomenten tot grote showcases met live publiek – onze ervaring, flexibiliteit en oog voor detail maken van uw lancering een krachtig statement.

Maak van uw lancering een belevenis die blijft hangen.
Kies voor impact, kies voor de Waerboom."""  # noqa: E501, RUF001
        concept.slogan = "Productlanceringen bij de Waerboom – Breng uw merk tot leven"  # noqa: RUF001
        concept.segment = event_models.Concept.SegmentType.B2B
        concept.name_nl = "Product Lanceringen"
        concept.save()

    def create_conferences_concept(self, organization):
        logger.info("Creating conferences concept for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="d3b27f49-36d0-464f-b79c-21f2d5c8a8e5",
        )

        seminar_concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "conferences.jpg",
        )
        self.add_card_image(
            image_name="conferences.jpg",
            image_path=seminar_concept_image,
            card=concept,
        )
        concept.card_description_nl = """Op zoek naar de ideale locatie voor uw volgende conferentie?
Bij de Waerboom bieden we een perfecte combinatie van comfort, moderne faciliteiten en persoonlijke service. Onze ruimtes zijn ontworpen om uw evenement vlot en succesvol te laten verlopen, of het nu gaat om een kleinschalige bijeenkomst of een groot congres.

✔️ Ruime, flexibel in te richten zalen met daglicht
✔️ State-of-the-art audiovisuele apparatuur en snelle wifi
✔️ Professionele ondersteuning tijdens uw event
✔️ Verzorgde catering met koffiepauzes, lunches en diners
✔️ Overnachtingsmogelijkheden en ruime parking

Met onze rustige ligging en sfeervolle setting zorgen wij voor een inspirerende omgeving waar ideeën, netwerken en samenwerking bloeien.

Maak uw conferentie tot een succes – bij de Waerboom."""  # noqa: E501, RUF001
        concept.slogan = "Conferenties bij de Waerboom – Inspirerende ontmoetingen in een stijlvolle omgeving"  # noqa: E501, RUF001
        concept.segment = event_models.Concept.SegmentType.B2B
        concept.name_nl = "Conferenties"
        concept.save()

    def create_teambulding_concept(self, organization):
        logger.info("Creating teambilding concept for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="9b4f3d18-5e1c-4a9d-9ec3-0a1fca17b0b1",
        )

        seminar_concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "teambuilding.jpg",
        )
        self.add_card_image(
            image_name="teambuilding.jpg",
            image_path=seminar_concept_image,
            card=concept,
        )
        concept.card_description_nl = """Wil je het teamgevoel versterken, communicatie verbeteren en samen onvergetelijke momenten beleven?
Bij de Waerboom organiseren we inspirerende teambuildings in een prachtige, rustige omgeving waar focus en plezier hand in hand gaan.

Of je kiest voor creatieve workshops, actieve outdoor uitdagingen, of een ontspannen dag vol gezelligheid en goede gesprekken – wij zorgen voor een programma op maat, inclusief catering en faciliteiten die jullie dag helemaal compleet maken.

🤝 Op maat gemaakte activiteiten voor elke groepsgrootte
🌳 Rustige, groene locatie met binnen- en buitenmogelijkheden
🍽️ Catering van ontbijt tot diner, aangepast aan jullie wensen
🎯 Professionele begeleiding en organisatie
🅿️ Vlotte bereikbaarheid en ruime parking

Bij de Waerboom investeren we in de kracht van teams, zodat jullie niet alleen plezier maken, maar ook echt dichter naar elkaar groeien.

Boost jullie teamspirit met een teambuilding bij de Waerboom!"""  # noqa: E501, RUF001
        concept.slogan = "Teambuildings bij de Waerboom – Samen sterk, samen succesvol"  # noqa: RUF001
        concept.segment = event_models.Concept.SegmentType.B2B
        concept.name_nl = "Teambuildings"
        concept.save()

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
            image_name="wedding.jpg",
            image_path=wedding_concept_image,
            card=wedding_concept,
        )
        wedding_concept.slogan = "Jullie droomhuwelijk begint bij de Waerboom"
        wedding_concept.card_description_nl = """Op zoek naar een locatie waar romantiek, elegantie en perfectie samenkomen?
Bij de Waerboom maken we van jullie trouwdag een onvergetelijke belevenis.

Van een intieme ceremonie in het groen tot een spetterend avondfeest in een stijlvolle zaal – wij zorgen voor elk detail, zodat jullie volop kunnen genieten van de mooiste dag van jullie leven.

💍 Ceremonie, receptie, diner & feest op één locatie
🌸 Sfeervolle tuinen en luxueuze zalen
🍽️ Fijne gastronomie op maat van jullie wensen
🎵 Dansfeest met professionele omkadering
🛌 Overnachtingsmogelijkheden voor jullie en jullie gasten

Of jullie nu dromen van een klassiek trouwfeest, een modern concept of een thema-event – ons ervaren team begeleidt jullie met liefde en zorg, van de eerste kennismaking tot het laatste dansnummer.

Jullie liefde verdient een unieke locatie.
Kies voor de Waerboom en vier in stijl."""  # noqa: E501, RUF001
        wedding_concept.segment = event_models.Concept.SegmentType.B2C
        wedding_concept.name_nl = "Trouwen"
        wedding_concept.save()

    def create_communion_party_concept(self, organization):
        logger.info("Creating communion party for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="f7c3e1ac-85ef-4e0a-b510-42cc81b1954e",
        )
        communion_party_concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "communion.jpg",
        )
        self.add_card_image(
            image_name="communion.jpg",
            image_path=communion_party_concept_image,
            card=concept,
        )
        concept.slogan = "Communie- en lentefeesten bij de Waerboom – Een dag vol glimlachen en herinneringen"  # noqa: E501, RUF001
        concept.card_description_nl = """Een communie- of lentefeest vier je maar één keer… en bij de Waerboom maken we er iets onvergetelijks van!
In een sfeervolle omgeving, met oog voor detail en zorg voor jong én oud, zorgen wij voor een feest waar iedereen van geniet – van de eerste toast tot het laatste dansje.

Onze prachtige locatie biedt alle troeven voor een zorgeloze en feestelijke dag: een feestmenu op maat, een stijlvolle zaal, en een buitenruimte waar kinderen zich volop kunnen uitleven.

🎈 Springkasteel en ruimte om te spelen
🍽️ Verzorgd buffet of feestmenu op kindermaat én voor volwassenen
🌷 Feestelijke setting met oog voor sfeer en details
🎉 Mogelijkheid tot animatie, DJ of fotobooth
🛏️ Overnachting mogelijk voor gasten van ver

Terwijl de kinderen zich amuseren, kunnen de volwassenen genieten van een glaasje, lekker eten en een ontspannen sfeer. Bij de Waerboom zorgen we ervoor dat het feest draait om wat écht telt: samen mooie herinneringen maken.

Een grote dag voor kleine feestvierders – en hun familie.
Vier het in stijl, vier het bij de Waerboom."""  # noqa: E501, RUF001
        concept.segment = event_models.Concept.SegmentType.B2C
        concept.name_nl = "Communie- of Lentefeesten"
        concept.save()

    def create_babyborrel_concept(self, organization):
        logger.info("Creating babyborrel concept for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="3f8c6e87-6cf3-47c1-8f1f-2e74e98e1a9f",
        )
        concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "babyborrel.jpg",
        )
        self.add_card_image(
            image_name="babyborrel.jpg",
            image_path=concept_image,
            card=concept,
        )
        concept.card_description_nl = """Een nieuw leven, een nieuw begin – dat verdient een bijzondere viering.
Bij de Waerboom organiseren we babyborrels in een sfeervol en kindvriendelijk kader, helemaal op maat van jullie wensen. Intiem of uitbundig, klassiek of eigentijds: wij zorgen voor een feest waar warmte, gezelligheid en zorg centraal staan.

🍼 Stijlvolle zalen of tuinfeest in openlucht
🧁 Verzorgde recepties, buffetten of zoete tafel
🎈 Speelhoek en springkasteel voor de kleinsten
🍾 Aperitiefmoment met bubbels en bites
💖 Een dag vol liefde, familie en mooie momenten

Terwijl jullie gasten genieten van een ontspannen sfeer en verfijnde catering, kunnen jullie in alle rust samen met jullie kleintje stralen. Alles wordt tot in de puntjes geregeld, zodat jullie volop kunnen genieten van het samenzijn.

Een warm welkom voor jullie kleine wonder.
Vier het leven bij de Waerboom."""  # noqa: E501, RUF001
        concept.slogan = "Vier het nieuwe leven bij de Waerboom – Babyborrels in een warme, stijlvolle setting"  # noqa: E501, RUF001
        concept.segment = event_models.Concept.SegmentType.B2C
        concept.name_nl = "Babyborrels"
        concept.save()

    def create_birthday_party_concept(self, organization):
        logger.info("Creating birthday party for organization %s", organization)
        concept, created = event_models.Concept.objects.get_or_create(
            organizer_id=organization.pk,
            public_key="12e4f3c7-8a3e-45b1-a6e3-5e4d9c55cf2f",
        )
        concept_image = os.path.join(  # noqa: PTH118
            settings.BASE_DIR,
            "data",
            "waerboom",
            "images",
            "concept",
            "birthday.png",
        )
        self.add_card_image(
            image_name="birthday.png",
            image_path=concept_image,
            card=concept,
        )
        concept.card_description_nl = """Een verjaardag of jubileum vier je niet zomaar… dat doe je in stijl, op een plek waar sfeer, kwaliteit en gastvrijheid samenkomen. De Waerboom biedt het perfecte decor voor een onvergetelijk feest, groot of intiem.

Laat je gasten genieten van een prachtige locatie in het groen, stijlvolle zalen op maat van jouw wensen, en een verzorgde catering die elk moment tot in de puntjes afmaakt. Of het nu gaat om een sprankelende verjaardag, een gouden jubileum of een andere mijlpaal – ons team staat klaar om jouw feest tot een unieke belevenis te maken.

🎉 Volledige ontzorging van A tot Z
🍷 Heerlijke menu’s en walking dinners
💃 Ruimte voor dans, muziek en gezelligheid
🌳 Charmante tuin en overnachtingsmogelijkheden

Maak van jouw viering een herinnering om te koesteren."""  # noqa: E501, RUF001
        concept.slogan = (
            "Vier jouw bijzondere dag bij de Waerboom – een onvergetelijke beleving!"  # noqa: RUF001
        )
        concept.segment = event_models.Concept.SegmentType.B2C
        concept.name_nl = "Verjaardagen of Jubileums"
        concept.save()

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
        styling.primary_button_color = "#26a69a"
        styling.primary_button_text_color = "#fff"

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

    def create_waerboom_website(self, organization):  # noqa: PLR0915
        logger.info("Creating website for organization %s", organization)
        wb_website, created = website_models.Website.objects.get_or_create(
            public_key="60923a27-67dd-475d-8a04-f692509e14b0",
        )
        wb_website.domain_name = "waerboom.com"
        wb_website.slogan = (
            "<i>Waer</i> samen vergaderen en feesten onvergetelijk wordt!"
        )
        wb_website.ask_segment = True
        wb_website.organization_id = organization.pk
        wb_website.save()

        home_page, created = website_models.Page.objects.get_or_create(
            website_id=wb_website.pk,
            name="Home",
            slug="home",
        )
        if created:
            home_page.publish_from = ITS_NOW
            home_page.ordering = 1
        home_page.banner_title = "Waerboom"
        home_page.banner_slogan = (
            "<i>Waer</i> samen vergaderen en feesten onvergetelijk wordt!"
        )
        banner_image = file_models.ImageFile.objects.filter(
            checksum="1a8cbb465ed49cf6244416418651175dd83ef125a127c9596747bc7a866c44fa",
        ).first()
        home_page.banner_image = banner_image
        home_page.save()

        concepts_page, concepts_page_created = (
            website_models.Page.objects.get_or_create(
                public_key="61277f46-71ce-4671-80af-93d4360e9ed2",
            )
        )

        concepts_page.name = "Jouw Evenement"
        concepts_page.website_id = wb_website.pk

        if concepts_page_created:
            concepts_page.publish_from = ITS_NOW
            concepts_page.ordering = 2

        concepts_page.banner_title = "Concepten"
        concepts_page.banner_slogan = (
            "Uw evenement bij Waerboom... <i>Waer</i>om zou je twijfelen?"
        )
        banner_image = file_models.ImageFile.objects.filter(
            checksum="a480e773718a68181141f76934f263e8d752fe55cf6cb5751b78e0760e2c601e",
        ).first()
        concepts_page.banner_image = banner_image
        concepts_page.save()

        concept_intro_image = file_models.ImageFile.objects.filter(
            checksum="e319ab811c6f0e37c75173c5f8defaca3b5ec3928fd18e31ada3a394f0b74db8",
        ).first()
        concept_intro_block, concept_intro_block_created = (
            website_models.ImageAndTextBlock.objects.get_or_create(
                public_key="1d4b277b-bba2-4337-881e-be54a2d3c8a8",
            )
        )
        if concept_intro_block_created:
            concept_intro_block.publish_from = ITS_NOW
        concept_intro_block.website_id = wb_website.pk
        concept_intro_block.background_color = "#FF9C35FF"
        concept_intro_block.rotate = -2
        concept_intro_block.image_id = concept_intro_image.pk
        concept_intro_block.margin_top = "-210px"
        concept_intro_block.name = "Eén locatie, eindeloze mogelijkheden"
        concept_intro_block.text = """
Van een intiem familiefeest tot een groots bedrijfsevent – bij de Waerboom vind je alles onder één dak.
Wij bieden stijlvolle zalen, verfijnde catering, een groene omgeving en professionele service voor elk type gelegenheid:

🎉 Verjaardagen, jubilea & trouwfeesten
🎤 Seminaries, vergaderingen & conferenties
🍷 Business events, teambuildings & productlanceringen
👨‍👩‍👧‍👦 Communiefeesten, babyborrels & lentefeesten
🎶 Hoevefeesten, dinnershows & zondagse gastronomische buffetten

Met onze jarenlange ervaring en persoonlijke aanpak maken we van elk moment een beleving op maat.

<b>Ontdek wat er mogelijk is – welkom bij de Waerboom.</b>
"""  # noqa: E501, RUF001
        concept_intro_block.save()
        website_models.PageBlock.objects.get_or_create(
            page_id=concepts_page.pk,
            block_id=concept_intro_block.pk,
            ordering=1,
        )

        concepts_block, events_block_created = (
            website_models.ConceptsBlock.objects.get_or_create(
                public_key="fb24f287-e241-495f-8c6f-5e2ea90f0e7d",
            )
        )
        if events_block_created:
            concepts_block.publish_from = ITS_NOW

        concepts_block.website_id = wb_website.pk
        concepts_block.save()

        website_models.PageBlock.objects.get_or_create(
            page_id=concepts_page.pk,
            block_id=concepts_block.pk,
            ordering=2,
        )

        events_page, events_page_created = website_models.Page.objects.get_or_create(
            public_key="70e65163-22d0-4386-a988-18f20898f91a",
        )

        events_page.website_id = wb_website.pk
        events_page.name = "Onze Evenementen"

        if events_page_created:
            events_page.ordering = 3
            events_page.publish_from = ITS_NOW

        events_page.banner_title = "Onze Evenementen"
        events_page.banner_slogan = (
            "<i>Waer</i> je ongetwijfeld met een goed gevoel op terugblikt..."
        )
        banner_image = file_models.ImageFile.objects.filter(
            checksum="27af94598dcc65b6efe0b4a08f0ad1ac8980832cf87da3fe593907273817dab2",
        ).first()
        events_page.banner_image = banner_image
        events_page.save()

        events_block, events_block_created = (
            website_models.EventsBlock.objects.get_or_create(
                website_id=wb_website.pk,
            )
        )
        if events_block_created:
            events_block.publish_from = ITS_NOW
            events_block.save()

        website_models.PageBlock.objects.get_or_create(
            page_id=events_page.pk,
            block_id=events_block.pk,
        )

    def create_address(self, organization):
        logger.info("Creating address for organization %s", organization)
        address, created = geography_models.Address.objects.get_or_create(
            public_key="7e9b55e8-279e-4f9b-89ae-d3b139d8d8d2",
        )

        address.street = "Jozef Mertensstraat"
        address.house_number = "140"
        address.city = "Groot-Bijgaarden"
        address.postal_code = "1702"
        address.country = "BE"
        address.save()

        organization_address, created = (
            organization_models.OrganizationAddress.objects.get_or_create(
                organization_id=organization.pk,
                address_id=address.pk,
            )
        )

    def create_one_dish(self, name):
        logger.info("Creating dish %s", name)
        dish, created = catering_models.Dish.objects.get_or_create(name=name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"{dish} created"))

        if dish.image_count == 0:
            from scaleos.catering.tasks import import_mealdb_dishes

            import_mealdb_dishes(dish.name)

    def create_dishes(self, organization):
        logger.info("Creating dishes for organization %s", organization)

        self.create_one_dish(name="Fish Soup (Ukha)")
        self.create_one_dish(name="15-minute chicken & halloumi burgers")
        self.create_one_dish(name="Fruit and Cream Cheese Breakfast Pastries")
        self.create_one_dish(name="Strawberries Romanoff")
        self.create_one_dish(name="Vietnamese Grilled Pork (bun-thit-nuong)")
        self.create_one_dish(name="Grilled Mac and Cheese Sandwich")
        self.create_one_dish(name="Crock Pot Chicken Baked Tacos")
        self.create_one_dish(name="Chicken Karaage")
        self.create_one_dish(name="Salted Caramel Cheescake")
        self.create_one_dish(name="Pilchard puttanesca")
        self.create_one_dish(name="Venetian Duck Ragu")
        self.create_one_dish(name="Clam chowder")
        self.create_one_dish(name="Broccoli & Stilton soup")
        self.create_one_dish(name="Tuna Nicoise")
        self.create_one_dish(name="Spaghetti Bolognese")
        self.create_one_dish(name="Spaghetti alla Carbonara")
        self.create_one_dish(name="Bigos (Hunters Stew)")
        self.create_one_dish(name="Portuguese fish stew (Caldeirada de peixe)")
        self.create_one_dish(name="Chicken Quinoa Greek Salad")

    def create_one_product(self, barcode):
        logger.info("Creating product for barcode %s", barcode)
        product, created = catering_models.Product.objects.get_or_create(
            barcode=barcode,
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"{product} created"))

    def create_products(self, organization):
        logger.info("Creating products for organization %s", organization)
        self.create_one_product("3256223411209")
        self.create_one_product("3024482270109")
        self.create_one_product("5411681014005")
        self.create_one_product("54491472")
        self.create_one_product("40822938")

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
        waerboom.card_description = """
Van een intiem familiefeest tot een groots bedrijfsevent – bij de Waerboom vind je alles onder één dak.
Wij bieden stijlvolle zalen, verfijnde catering, een groene omgeving en professionele service voor elk type gelegenheid:

🎉 Verjaardagen, jubilea & trouwfeesten
🎤 Seminaries, vergaderingen & conferenties
🍷 Business events, teambuildings & productlanceringen
👨‍👩‍👧‍👦 Communiefeesten, babyborrels & lentefeesten
🎶 Hoevefeesten, dinnershows & zondagse gastronomische buffetten

Met onze jarenlange ervaring en persoonlijke aanpak maken we van elk moment een beleving op maat.

<b>Ontdek wat er mogelijk is – welkom bij de Waerboom.</b>
"""  # noqa: E501, RUF001
        waerboom.slug = "waerboom"
        waerboom.published_on = ITS_NOW
        waerboom.save()

        upload_files(waerboom, organization_file_dir="waerboom")
        self.create_buildings(waerboom)
        self.create_styling(waerboom)
        self.create_address(waerboom)

        self.create_dishes(waerboom)
        self.create_products(waerboom)

        # CREATE CONCEPTS
        # B2B
        self.create_meeting_concept(waerboom)
        self.create_employee_party(waerboom)
        self.create_seminar_concept(waerboom)
        self.create_teambulding_concept(waerboom)
        self.create_conferences_concept(waerboom)
        self.create_product_launch_concept(waerboom)
        self.create_business_breakfast_club_concept(waerboom)
        self.create_business_lunch(waerboom)
        # B2C
        self.create_wedding_concept(waerboom)
        self.create_communion_party_concept(waerboom)
        self.create_birthday_party_concept(waerboom)
        self.create_babyborrel_concept(waerboom)
        # BOTH
        self.create_hoevefeesten_concept(waerboom)
        self.create_dinner_and_dance_concept(waerboom)
        self.create_brunch_concept(waerboom)

        self.create_waerboom_owners(waerboom)
        self.create_waerboom_payment_methods(waerboom)
        self.create_waerboom_website(waerboom)

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
