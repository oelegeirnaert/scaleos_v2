import datetime

import pytest
from dateutil.relativedelta import relativedelta
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
def test_event_has_free_capacity(faker):
    activate("nl")
    event = event_factories.EventFactory.create()

    assert event.free_spots == "∞"

    event.maximum_number_of_guests = 100

    assert event.free_spots == 100
    assert event.free_percentage == 100
    assert event.reserved_percentage == 0
    assert event.reserved_spots == 0

    event_reservation1_reservation_lines = (
        reservation_factories.ReservationLineFactory.create_batch(
            2,
            amount=15,
        )
    )
    event_reservation1 = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    event_reservation1.lines.set(event_reservation1_reservation_lines)
    assert event.reservations.count() == 1
    assert event.free_spots == 70
    assert event.free_percentage == 70
    assert event.reserved_percentage == 30
    assert event.reserved_spots == 30

    event_reservation2_reservation_lines = (
        reservation_factories.ReservationLineFactory.create_batch(2, amount=5)
    )
    event_reservation2 = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    event_reservation2.lines.set(event_reservation2_reservation_lines)
    assert event.free_spots == 60
    assert event.free_percentage == 60
    assert event.reserved_percentage == 40
    assert event.reserved_spots == 40
    assert event.over_reserved_spots == 0

    event_reservation3_reservation_lines = (
        reservation_factories.ReservationLineFactory.create_batch(6, amount=10)
    )
    event_reservation3 = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    event_reservation3.lines.set(event_reservation3_reservation_lines)
    assert event.free_spots == 0
    assert event.free_percentage == 0
    assert event.reserved_percentage == 100
    assert event.reserved_spots == 100
    assert event.over_reserved_spots == 0

    event_reservation4_reservation_lines = (
        reservation_factories.ReservationLineFactory.create_batch(5, amount=2)
    )
    event_reservation4 = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    event_reservation4.lines.set(event_reservation4_reservation_lines)
    assert event.free_spots == 0
    assert event.free_percentage == 0
    assert event.reserved_percentage == 100
    assert event.reserved_spots == 110
    assert event.over_reserved_spots == 10


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
    status = single_event.get_status(its_now=the_now)
    assert status == event_models.SingleEvent.STATUS.UNKNOWN

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
    status = single_event.get_status(its_now=the_now)
    assert status == event_models.SingleEvent.STATUS.ENDED

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
    status = single_event.get_status(its_now=the_now)
    assert status == event_models.SingleEvent.STATUS.UPCOMING

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
    status = single_event.get_status(its_now=the_now)
    assert status == event_models.SingleEvent.STATUS.UPCOMING

    single_event.starting_at = yesterday
    single_event.ending_on = tomorrow
    status = single_event.get_status(its_now=the_now)
    assert status == event_models.SingleEvent.STATUS.ONGOING


@pytest.mark.django_db
def test_event_has_a_current_price_matrix(faker):
    from scaleos.payments.tests import model_factories as payment_factories

    today = timezone.make_aware(
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
    two_years_ago = today - relativedelta(years=2)
    last_year = today - relativedelta(years=1)
    next_year = today + relativedelta(years=1)
    in_two_years = today + relativedelta(years=2)
    concept = event_factories.ConceptFactory()
    price_matrixes = payment_factories.PriceMatrixFactory.create_batch(6)
    event = event_factories.EventFactory(concept_id=concept.pk)

    assert hasattr(event, "current_price_matrix")
    assert event.current_price_matrix is None

    always_valid_price_matrix = event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        price_matrix_id=price_matrixes[0].pk,
    )
    assert hasattr(event, "current_price_matrix")
    assert event.current_price_matrix.id == always_valid_price_matrix.price_matrix.pk

    event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        price_matrix_id=price_matrixes[1].pk,
    )

    assert event.current_price_matrix is None, (
        "because we do not know which one to choose"
    )

    as_from_last_year_price_matrix = event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        valid_from=two_years_ago,
        price_matrix_id=price_matrixes[2].pk,
    )
    assert hasattr(event, "current_price_matrix")
    assert (
        event.current_price_matrix.id == as_from_last_year_price_matrix.price_matrix.pk
    )

    event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        valid_from=two_years_ago,
        valid_till=last_year,
        price_matrix_id=price_matrixes[3].pk,
    )
    current_concept_price_matrix = event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        valid_from=last_year,
        valid_till=next_year,
        price_matrix_id=price_matrixes[4].pk,
    )
    event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        valid_from=next_year,
        valid_till=in_two_years,
        price_matrix_id=price_matrixes[5].pk,
    )
    assert event.current_price_matrix.id == current_concept_price_matrix.price_matrix.pk
