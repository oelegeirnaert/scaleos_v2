import datetime

import pytest
from django.utils import timezone
from django.utils.translation import activate

from scaleos.events import models as event_models
from scaleos.events.tests import model_factories as event_factories
from scaleos.reservations.tests import model_factories as reservation_factories


@pytest.mark.django_db
def test_brunchconcept_can_generate_events(faker):
    brunch_concept = event_factories.BrunchConceptFactory.create()
    from_date = datetime.date(year=2025, month=2, day=1)
    to_date = datetime.date(year=2025, month=3, day=1)
    weekday = 7
    brunch_concept.generate(from_date, to_date, weekday)
    assert brunch_concept.events.count() == 4, "4 sundays in feb 2025"


@pytest.mark.django_db
def test_brunch_has_free_capacity(faker):
    activate("nl")
    brunch_event = event_factories.BrunchEventFactory.create()

    assert brunch_event.free_spots == "ongelimiteerd"

    brunch_event.maximum_number_of_guests = 100

    assert brunch_event.free_spots == 100
    assert brunch_event.free_percentage == 100
    assert brunch_event.reserved_percentage == 0
    assert brunch_event.reserved_spots == 0

    brunch_reservations = reservation_factories.BrunchReservationFactory.create_batch(
        4,
        brunch_event_id=brunch_event.pk,
    )
    brunch_reservations[0].amount = 30
    brunch_reservations[0].save()
    assert brunch_event.free_spots == 70
    assert brunch_event.free_percentage == 70
    assert brunch_event.reserved_percentage == 30
    assert brunch_event.reserved_spots == 30

    brunch_reservations[1].amount = 10
    brunch_reservations[1].save()
    assert brunch_event.free_spots == 60
    assert brunch_event.free_percentage == 60
    assert brunch_event.reserved_percentage == 40
    assert brunch_event.reserved_spots == 40
    assert brunch_event.over_reserved_spots == 0

    brunch_reservations[2].amount = 60
    brunch_reservations[2].save()
    assert brunch_event.free_spots == 0
    assert brunch_event.free_percentage == 0
    assert brunch_event.reserved_percentage == 100
    assert brunch_event.reserved_spots == 100
    assert brunch_event.over_reserved_spots == 0

    brunch_reservations[3].amount = 10
    brunch_reservations[3].save()
    assert brunch_event.free_spots == 0
    assert brunch_event.free_percentage == 0
    assert brunch_event.reserved_percentage == 100
    assert brunch_event.reserved_spots == 110
    assert brunch_event.over_reserved_spots == 10


@pytest.mark.django_db
def test_if_single_event_has_a_name(faker):
    expected_name = "single event"
    single_event = event_factories.SingleEventFactory.create(name=expected_name)
    assert expected_name == str(single_event)

    mkdate = datetime.datetime(year=2025, month=2, day=13, hour=11, minute=00)
    concept = event_factories.ConceptFactory.create(name="Brunch")
    single_event.concept_id = concept.pk
    single_event.starting_at = mkdate
    single_event.save()
    assert str(single_event) == "Brunch 2025-02-13"


@pytest.mark.django_db
def test_wedding_concept_event_generation(faker):
    wedding_concept = event_factories.WeddingConceptFactory.create()
    assert wedding_concept.generate_events()


@pytest.mark.django_db
def test_dinner_and_dance_concept_event_generation(faker):
    dinner_and_dance_concept = event_factories.DinnerAndDanceConceptFactory.create()
    assert dinner_and_dance_concept.generate_events()


@pytest.mark.django_db
def test_status_of_single_event(faker):
    single_event = event_factories.SingleEventFactory.create()
    assert single_event.status == event_models.SingleEvent.STATUS.UNKNOWN, (
        "because no dates are set."
    )

    the_now = timezone.make_aware(
        datetime.datetime(
            year=2025,
            month=3,
            day=5,
            hour=11,
            minute=00,
            second=00,
        ),
        timezone.get_default_timezone(),
    )
    assert (
        single_event.get_status(its_now=the_now)
        == event_models.SingleEvent.STATUS.UNKNOWN
    )

    yesterday = timezone.make_aware(
        datetime.datetime(
            year=2025,
            month=3,
            day=4,
            hour=11,
            minute=00,
            second=00,
        ),
        timezone.get_default_timezone(),
    )
    single_event.starting_at = yesterday
    single_event.ending_on = yesterday
    assert (
        single_event.get_status(its_now=the_now)
        == event_models.SingleEvent.STATUS.ENDED
    )

    tomorrow = timezone.make_aware(
        datetime.datetime(
            year=2025,
            month=3,
            day=6,
            hour=11,
            minute=00,
            second=00,
        ),
        timezone.get_default_timezone(),
    )
    single_event.starting_at = tomorrow
    single_event.ending_on = tomorrow
    assert (
        single_event.get_status(its_now=the_now)
        == event_models.SingleEvent.STATUS.UPCOMING
    )

    tomorrow = timezone.make_aware(
        datetime.datetime(
            year=2025,
            month=3,
            day=6,
            hour=11,
            minute=00,
            second=00,
        ),
        timezone.get_default_timezone(),
    )
    single_event.starting_at = tomorrow
    single_event.ending_on = None
    assert (
        single_event.get_status(its_now=the_now)
        == event_models.SingleEvent.STATUS.UPCOMING
    )

    single_event.starting_at = yesterday
    single_event.ending_on = tomorrow
    assert (
        single_event.get_status(its_now=the_now)
        == event_models.SingleEvent.STATUS.ONGOING
    )
