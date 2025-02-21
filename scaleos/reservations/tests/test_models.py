import logging

import pytest
from moneyed import EUR
from moneyed import Money

from scaleos.events.tests import model_factories as event_factories
from scaleos.hr.tests import model_factories as hr_factories
from scaleos.reservations.tests import model_factories as reservation_factories

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


# @pytest.mark.django_db
# def test_event_can_have_other_pricematrix_than_concept(faker):
#    assert False, "implement me"
