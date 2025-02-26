import logging

import pytest
from moneyed import EUR
from moneyed import Money

from scaleos.events.tests import model_factories as event_factories
from scaleos.hr.tests import model_factories as hr_factories
from scaleos.payments.tests import model_factories as payment_factories
from scaleos.reservations import models as reservation_models
from scaleos.reservations.tests import model_factories as reservation_factories
from scaleos.shared.mixins import ITS_NOW
from scaleos.users.tests import model_factories as user_factories

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_brunch_reservation_for_waerboom(faker):
    logger.setLevel(logging.DEBUG)
    from scaleos.payments.tests.model_factories import AgePriceMatrixFactory
    from scaleos.payments.tests.model_factories import AgePriceMatrixItemFactory
    from scaleos.payments.tests.model_factories import PriceFactory

    brunch_concept = event_factories.BrunchConceptFactory.create()
    age_price_matrix = AgePriceMatrixFactory.create()

    the_baby_price = Money(0.0, EUR)
    baby_price = PriceFactory.create(current_price=the_baby_price)
    baby_price_matrix_item = AgePriceMatrixItemFactory.create(
        till_age=4,
        price_id=baby_price.pk,
        age_price_matrix_id=age_price_matrix.pk,
    )

    the_children_price = Money(10, EUR)
    children_price = PriceFactory.create(current_price=the_children_price)
    children_price_matrix_item = AgePriceMatrixItemFactory.create(
        from_age=5,
        till_age=12,
        price_id=children_price.pk,
        age_price_matrix_id=age_price_matrix.pk,
    )

    the_adolescent_price = Money(20, EUR)
    adolescent_price = PriceFactory.create(current_price=the_adolescent_price)
    adolescent_price_matrix_item = AgePriceMatrixItemFactory.create(
        from_age=13,
        till_age=16,
        price_id=adolescent_price.pk,
        age_price_matrix_id=age_price_matrix.pk,
    )

    the_adult_price = Money(30, EUR)
    adult_price = PriceFactory.create(current_price=the_adult_price)
    adult_price_matrix_item = AgePriceMatrixItemFactory.create(
        from_age=17,
        price_id=adult_price.pk,
        age_price_matrix_id=age_price_matrix.pk,
    )

    event_factories.ConceptPriceMatrixFactory.create(
        concept_id=brunch_concept.pk,
        price_matrix_id=age_price_matrix.pk,
    )
    assert brunch_concept.current_price_matrix, "check if the brunc has a price matrix"

    brunch_event = event_factories.BrunchEventFactory.create(
        concept_id=brunch_concept.pk,
    )
    brunch_reservation = reservation_factories.BrunchReservationFactory.create(
        event_id=brunch_event.pk,
    )

    person = hr_factories.PersonFactory.create()

    brunch_reservation.person_id = person.pk
    brunch_reservation.save()

    assert Money(0, EUR) == brunch_reservation.total_price, (
        "because we haven't any reservation lines yet"
    )
    assert brunch_event.current_price_matrix, (
        "We must have a price matrix in order to be able to do the calculations"
    )

    brunch_reservation.used_price_matrix = brunch_event.current_price_matrix
    brunch_reservation.save()

    number_of_babies = 3
    baby_reservation = reservation_factories.ReservationLineFactory.create(
        reservation_id=brunch_reservation.pk,
        amount=number_of_babies,
        price_matrix_item_id=baby_price_matrix_item.pk,
    )
    assert number_of_babies * the_baby_price == baby_reservation.total_price

    number_of_children = 5
    children_reservation = reservation_factories.ReservationLineFactory.create(
        reservation_id=brunch_reservation.pk,
        amount=number_of_children,
        price_matrix_item_id=children_price_matrix_item.pk,
    )
    assert the_children_price * number_of_children == children_reservation.total_price

    number_of_adolescents = 2
    adolescent_reservation = reservation_factories.ReservationLineFactory.create(
        reservation_id=brunch_reservation.pk,
        amount=number_of_adolescents,
        price_matrix_item_id=adolescent_price_matrix_item.pk,
    )
    assert (
        number_of_adolescents * the_adolescent_price
        == adolescent_reservation.total_price
    )

    number_of_adults = 4
    adults_reservation = reservation_factories.ReservationLineFactory.create(
        reservation_id=brunch_reservation.pk,
        amount=number_of_adults,
        price_matrix_item_id=adult_price_matrix_item.pk,
    )
    assert number_of_adults * the_adult_price == adults_reservation.total_price

    assert (
        baby_reservation.total_price
        + children_reservation.total_price
        + adolescent_reservation.total_price
        + adults_reservation.total_price
        == brunch_reservation.total_price
    )


@pytest.mark.django_db
def test_brunch_reservationline_for_waerboom_has_min_max_persons(faker):
    from scaleos.payments.tests.model_factories import AgePriceMatrixItemFactory

    minimum = 8
    maximum = 13
    age_price_matrix_item = AgePriceMatrixItemFactory.create(
        minimum_persons=minimum,
        maximum_persons=maximum,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        price_matrix_item_id=age_price_matrix_item.pk,
    )
    assert hasattr(reservation_line, "minimum_amount")
    assert hasattr(reservation_line, "maximum_amount")
    assert minimum == reservation_line.minimum_amount
    assert maximum == reservation_line.maximum_amount


@pytest.mark.django_db
def test_brunch_reservationline_for_waerboom_cannot_exceed_total_availble_places(faker):
    from scaleos.payments.tests.model_factories import AgePriceMatrixItemFactory

    max_spots = 100
    line_max = 5
    brunch = event_factories.BrunchEventFactory.create(
        maximum_number_of_guests=max_spots,
    )
    assert max_spots == brunch.free_spots
    age_price_matrix_item = AgePriceMatrixItemFactory.create(
        maximum_persons=line_max,
    )
    event_reservation = reservation_factories.EventReservationFactory(
        event_id=brunch.pk,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        price_matrix_item_id=age_price_matrix_item.pk,
        reservation_id=event_reservation.pk,
    )
    assert line_max == reservation_line.maximum_amount

    max_spots = 3
    small_brunch = event_factories.BrunchEventFactory.create(
        maximum_number_of_guests=max_spots,
    )
    very_large_event_reservation = reservation_factories.EventReservationFactory(
        event_id=small_brunch.pk,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        price_matrix_item_id=age_price_matrix_item.pk,
        reservation_id=very_large_event_reservation.pk,
    )
    assert max_spots == small_brunch.free_spots
    assert max_spots == reservation_line.maximum_amount, (
        f"because we only have {brunch.free_spots} free spots in the event"
    )

    brunch_unlimited_seats = event_factories.BrunchEventFactory.create(
        maximum_number_of_guests=None,
    )
    unlimited_event_reservation = reservation_factories.EventReservationFactory(
        event_id=brunch_unlimited_seats.pk,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        price_matrix_item_id=age_price_matrix_item.pk,
        reservation_id=unlimited_event_reservation.pk,
    )
    assert brunch_unlimited_seats.free_spots == "∞"
    assert reservation_line.maximum_amount is None, (
        "because we only have unlimited free spots in the event"
    )


@pytest.mark.django_db
def test_reservation_has_total_amount(faker):
    reservation = reservation_factories.ReservationFactory.create()
    assert reservation.total_amount is None
    reservation_factories.ReservationLineFactory.create_batch(
        3,
        reservation_id=reservation.pk,
        amount=3,
    )
    assert reservation.total_amount == 9


@pytest.mark.django_db
def test_reservation_is_human_verified(faker):
    the_email = "my_email@hotmail.com"

    user = user_factories.UserFactory(email=the_email)
    user_factories.EmailAddressFactory(user=user, email=user.email)

    reservation = reservation_factories.ReservationFactory(user=user)
    assert reservation.verified_email_address == the_email


@pytest.mark.django_db
def test_reservation_is_not_human_verified(faker):
    the_email = "my_email@hotmail.com"

    user = user_factories.UserFactory(email=the_email)

    reservation = reservation_factories.ReservationFactory(user=user)
    assert reservation.verified_email_address is None


@pytest.mark.django_db
def test_reservation_finish(faker):
    an_email = "my_reservation_finish@hotmail.com"
    reservation = reservation_factories.ReservationFactory()
    assert reservation.finish(request=None, confirmation_email_address=an_email)
    assert not (
        reservation.finish(request=None, confirmation_email_address=an_email)
    ), "because it is already finished"


@pytest.mark.django_db
def test_reservation_requester_confirm(faker):
    reservation = reservation_factories.ReservationFactory()
    reservation.requester_confirm()
    assert reservation.requester_confirmed
    assert not reservation.requester_confirm(), "because it is already confirmed"


@pytest.mark.django_db
def test_reservation_organization_confirm(faker):
    reservation = reservation_factories.ReservationFactory()
    reservation.organization_confirm()
    assert reservation.organization_confirmed
    assert not reservation.organization_confirm(), "because it is already confirmed"


@pytest.mark.django_db
def test_reservation_is_statusses(faker):
    the_email = "my_email@hotmail.com"

    user = user_factories.UserFactory(email=the_email)

    reservation = reservation_factories.ReservationFactory(user=user)
    assert reservation.verified_email_address is None

    assert reservation.finished_on is None
    assert reservation.status == reservation_models.Reservation.STATUS.IN_PROGRESS
    reservation.finished_on = ITS_NOW
    assert (
        reservation.status == reservation_models.Reservation.STATUS.NEEDS_VERIFICATION
    )
    reservation.requester_confirmed_on = ITS_NOW
    assert reservation.organization_confirmed_on is None
    assert reservation.status == reservation_models.Reservation.STATUS.TO_BE_CONFIRMED


@pytest.mark.django_db
def test_reservation_payment_request(faker):
    hundred_euro = Money(100, EUR)
    price = payment_factories.PriceFactory.create(
        current_price=hundred_euro,
        includes_vat=False,
        vat_percentage=21,
    )
    assert Money(121.00, "EUR") == price.vat_included

    age_price_matrix = payment_factories.AgePriceMatrixFactory()
    age_price_matrix_item = payment_factories.AgePriceMatrixItemFactory(
        age_price_matrix_id=age_price_matrix.pk,
        price_id=price.pk,
    )
    brunch_concept = event_factories.BrunchConceptFactory()
    event_factories.ConceptPriceMatrixFactory(
        price_matrix_id=age_price_matrix.pk,
        concept_id=brunch_concept.pk,
    )
    brunch_event = event_factories.BrunchEventFactory(concept_id=brunch_concept.pk)
    assert brunch_event.current_price_matrix

    reservation = reservation_factories.EventReservationFactory(
        event_id=brunch_event.pk,
    )
    reservation_factories.ReservationLineFactory(
        reservation_id=reservation.pk,
        amount=1,
        price_matrix_item_id=age_price_matrix_item.pk,
    )
    assert reservation.lines.count() == 1

    assert reservation.total_price_vat_included.amount == 121
    reservation.organization_confirm()
    assert reservation.payment_request
    assert reservation.payment_request.to_pay
    assert reservation.payment_request.to_pay.vat_included.amount == 121


# @pytest.mark.django_db
# def test_event_can_have_other_pricematrix_than_concept(faker):
#    assert False, "implement me"
