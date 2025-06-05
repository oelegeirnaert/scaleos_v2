from datetime import UTC
from datetime import datetime
from decimal import Decimal

import pytest
from django.utils import timezone
from django.utils.translation import activate
from moneyed import EUR
from moneyed import Money

from scaleos.events.tests import model_factories as event_factories
from scaleos.organizations.tests import model_factories as organization_factories
from scaleos.payments import models as payment_models
from scaleos.payments.tests import model_factories as payment_factories
from scaleos.reservations.tests import model_factories as reservation_factories


@pytest.mark.django_db
class TestPrice:
    def test_price_format(self):
        free = payment_factories.PriceFactory.create(vat_included=None)
        assert str(free) == "free"

        free_item = Money(0, EUR)
        free = payment_factories.PriceFactory.create(vat_included=free_item)
        assert str(free) == "free"

        two_euro = Money(2, EUR)
        price = payment_factories.PriceFactory.create(vat_included=two_euro)
        assert str(price) == "€2.00 (vat included)"

        two_euro = Money(2.31, EUR)
        price = payment_factories.PriceFactory.create(vat_included=two_euro)
        assert str(price) == "€2.31 (vat included)"

        activate("nl")
        assert str(price) == "€ 2,31 (btw inbegrepen)"

@pytest.mark.django_db
def test_price_from_product_remains_the_same_after_multiplying(faker):
    """
    If we need to multiply a product, it should return a new instance of the multiplied price.
    Otherwise we are changing the price of the product which is not the prupose
    """  # noqa: E501

    amount = Money(8, EUR)
    product_price = payment_factories.PriceFactory.create(
        vat_included=amount,
    )
    assert product_price.vat_included == amount
    multiplied_price = product_price.multiply(5)
    assert product_price.vat_included == amount
    assert multiplied_price.vat_included == Money(40, EUR)

    amount = Money(100, EUR)
    product_price = payment_factories.PriceFactory.create(
        vat_included=amount,
    )
    assert product_price.vat_included == amount
    multiplied_price = product_price.multiply(2)
    assert product_price.vat_included == amount
    assert multiplied_price.vat_included == Money(200, EUR)


@pytest.mark.django_db
def test_price_can_be_summed_up(faker):
    price1 = payment_factories.PriceFactory.create(
        vat_included=Money(121.00, EUR),
        vat_excluded=Money(100.00, EUR),
    )

    price2 = payment_factories.PriceFactory.create(
        vat_included=Money(121.00, EUR),
        vat_excluded=Money(100.00, EUR),
    )

    total_price = payment_models.Price()
    total_price.plus(price1)
    total_price.plus(price2)
    assert total_price.vat_included == Money(242.00, EUR)
    assert total_price.vat_excluded == Money(200.00, EUR)
    assert total_price.vat == Money(42.00, EUR)


@pytest.mark.django_db
def test_price_with_different_vats_can_be_summed_up_and_have_all_vats_in_new_price(
    faker,
):
    hundred_euro = Money(100, EUR)
    price1 = payment_factories.PriceFactory.create()

    payment_factories.VATPriceLineFactory.create(
        price_id=price1.pk,
        input_price=hundred_euro,
        includes_vat=True,
        vat_percentage=6,
    )
    payment_factories.VATPriceLineFactory.create(
        price_id=price1.pk,
        input_price=hundred_euro,
        includes_vat=True,
        vat_percentage=12,
    )
    price1.refresh_from_db()
    assert price1.vat_included == Money(200, EUR)

    price2 = payment_factories.PriceFactory.create()

    payment_factories.VATPriceLineFactory.create(
        price_id=price2.pk,
        input_price=hundred_euro,
        includes_vat=True,
        vat_percentage=12,
    )
    payment_factories.VATPriceLineFactory.create(
        price_id=price2.pk,
        input_price=hundred_euro,
        includes_vat=True,
        vat_percentage=21,
    )
    price2.refresh_from_db()
    assert price2.vat_included == Money(200, EUR)

    total_price = payment_factories.PriceFactory.create(
        vat_included=None,
        vat_excluded=None,
    )
    total_price.plus(price1)
    total_price.plus(price2)

    assert total_price.vat_included == Money(400, EUR)
    vat_lines = total_price.vat_lines.count()
    assert vat_lines == 4, f"1 at 6%, 2 at 12% and 1 at 21%, we have {vat_lines} "





@pytest.mark.django_db
def test_price_vat_excercices(faker):
    # Based on: https://vatcalculator.eu/belgium-vat-calculator/
    vat_price_line = payment_factories.VATPriceLineFactory.create(
        input_price=Money(25, EUR),
        includes_vat=False,
        vat_percentage=21,
    )
    assert vat_price_line.vat_excluded == Money(25, EUR)
    assert vat_price_line.vat == Money(5.25, EUR)
    assert vat_price_line.vat_included == Money(30.25, EUR)

    vat_price_line2 = payment_factories.VATPriceLineFactory.create(
        input_price=Money(100, EUR),
        includes_vat=True,
        vat_percentage=21,
    )
    assert round(Decimal("82.64"), 2) == round(vat_price_line2.vat_excluded.amount, 2)
    assert round(Decimal("17.36"), 2) == round(vat_price_line2.vat.amount, 2)
    assert round(Decimal("100.00"), 2) == round(vat_price_line2.vat_included.amount, 2)

    vat_price_line3 = payment_factories.VATPriceLineFactory.create(
        input_price=Money(75.33, EUR),
        includes_vat=False,
        vat_percentage=6,
    )
    assert round(Decimal("75.33"), 2) == round(vat_price_line3.vat_excluded.amount, 2)
    assert round(Decimal("4.52"), 2) == round(vat_price_line3.vat.amount, 2)
    assert round(Decimal("79.85"), 2) == round(vat_price_line3.vat_included.amount, 2)

    vat_price_line4 = payment_factories.VATPriceLineFactory.create(
        input_price=Money(2049.16, EUR),
        includes_vat=True,
        vat_percentage=6,
    )
    assert round(Decimal("1933.17"), 2) == round(vat_price_line4.vat_excluded.amount, 2)
    assert round(Decimal("115.99"), 2) == round(vat_price_line4.vat.amount, 2)
    assert round(Decimal("2049.16"), 2) == round(vat_price_line4.vat_included.amount, 2)


@pytest.mark.django_db
def test_price_history(faker):
    price = payment_factories.PriceFactory.create()

    assert price.history.count() == 1
    price.vat_included = Money(30, EUR)
    price.save()
    assert price.history.count() == 2

    price.vat_included = Money(35, EUR)
    price.save()
    assert price.history.count() == 3
    assert price.previous_price

    price.vat_included = Money(40, EUR)
    price.save()
    assert price.history.count() == 4
    assert price.previous_price


@pytest.mark.django_db
def test_age_price_matrix_item_to_string(faker):
    activate("en")
    matrix = payment_factories.AgePriceMatrixFactory(name="brunch prijzen 2024")
    baby = payment_factories.AgePriceMatrixItemFactory(
        from_age=0,
        till_age=10,
        age_price_matrix_id=matrix.pk,
    )
    assert str(baby) == "brunch prijzen 2024 (0 year - 10 year): Free"

    grannies = payment_factories.AgePriceMatrixItemFactory(
        from_age=80,
        till_age=None,
        age_price_matrix_id=matrix.pk,
    )
    payment_factories.PriceFactory(
        vat_included=Money(10, EUR),
        unique_origin=grannies,
    )
    activate("nl")
    assert (
        str(grannies)
        == "brunch prijzen 2024 (80 jaar - ... ): € 10,00 (btw inbegrepen)"
    )

    adults = payment_factories.AgePriceMatrixItemFactory(
        from_age=18,
        till_age=65,
        age_price_matrix_id=matrix.pk,
    )
    payment_factories.PriceFactory(
        vat_included=Money(20, EUR),
        unique_origin=adults,
    )
    activate("nl")
    assert (
        str(adults)
        == "brunch prijzen 2024 (18 jaar - 65 jaar): € 20,00 (btw inbegrepen)"
    )


@pytest.mark.django_db
class TestEventReservationPaymentSettings:
    def test_get_conditions_text_no_conditions(self):
        organization = organization_factories.OrganizationFactory()
        settings = payment_factories.EventReservationPaymentSettingsFactory(
            organization=organization,
        )
        event = event_factories.SingleEventFactory(
            starting_at=timezone.make_aware(datetime(2024, 1, 1, 10, 0, 0)),
            ending_on=timezone.make_aware(datetime(2024, 1, 1, 12, 0, 0)),
            concept__organizer_id=organization.pk,
        )
        event_reservation = reservation_factories.EventReservationFactory(event=event)
        assert (
            settings.get_conditions_text(event_reservation) == "no conditions defined"
        )

    def test_get_conditions_text_with_conditions(self):
        organization = organization_factories.OrganizationFactory()
        settings = payment_factories.EventReservationPaymentSettingsFactory(
            organization=organization,
        )
        event = event_factories.SingleEventFactory(
            starting_at=timezone.make_aware(datetime(2024, 1, 1, 10, 0, 0)),
            ending_on=timezone.make_aware(datetime(2024, 1, 1, 12, 0, 0)),
            concept__organizer=organization,
        )
        event_reservation = reservation_factories.EventReservationFactory(event=event)

        age_price_matrix_item = payment_factories.AgePriceMatrixItemFactory()
        reservation_factories.ReservationLineFactory(
            reservation=event_reservation,
            amount=2,
            price_matrix_item_id=age_price_matrix_item.pk,
        )
        payment_factories.PriceFactory(
            vat_included=Money(10, EUR),
            unique_origin=age_price_matrix_item,
        )

        condition1 = payment_factories.EventReservationPaymentConditionFactory(
            event_reservation_payment_settings=settings,
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.FULL_PRICE,
            to_be_paid_time_amount=2,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.DAYS,
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_START_OF_EVENT,
        )
        condition2 = payment_factories.EventReservationPaymentConditionFactory(
            event_reservation_payment_settings=settings,
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.PERCENTAGE_OF_TOTAL_PRICE,
            percentage_of_total_price=50,
            to_be_paid_time_amount=1,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.WEEKS,
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_START_OF_EVENT,
        )
        condition1_price = condition1.get_price(event_reservation)
        condition2_price = condition2.get_price(event_reservation)
        assert condition1_price, "We should have a price for condition1"
        assert condition2_price, "We should have a price for condition2"
        expected_text = "<ul><li>50.00% of total price to be paid 1 weeks before the start of the event</li><li>Full price to be paid 2 days before the start of the event</li></ul>"  # noqa: E501
        assert settings.get_conditions_text(event_reservation) == expected_text

    def test_get_conditions_no_event(self):
        organization = organization_factories.OrganizationFactory()
        settings = payment_factories.EventReservationPaymentSettingsFactory(
            organization=organization,
        )
        event_reservation = reservation_factories.EventReservationFactory(event=None)
        payment_factories.EventReservationPaymentConditionFactory(
            event_reservation_payment_settings=settings,
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.FULL_PRICE,
            to_be_paid_time_amount=2,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.DAYS,
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_START_OF_EVENT,
        )
        assert settings.get_conditions(event_reservation) == {}

    def test_get_conditions_with_conditions(self):
        organization = organization_factories.OrganizationFactory()
        settings = payment_factories.EventReservationPaymentSettingsFactory(
            organization=organization,
        )
        event = event_factories.SingleEventFactory(
            starting_at=timezone.make_aware(datetime(2024, 1, 1, 10, 0, 0), UTC),
            ending_on=timezone.make_aware(datetime(2024, 1, 1, 12, 0, 0), UTC),
            concept__organizer=organization,
        )
        event_reservation = reservation_factories.EventReservationFactory(event=event)
        payment_factories.EventReservationPaymentConditionFactory(
            event_reservation_payment_settings=settings,
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.FULL_PRICE,
            to_be_paid_time_amount=2,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.DAYS,
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_START_OF_EVENT,
        )
        payment_factories.EventReservationPaymentConditionFactory(
            event_reservation_payment_settings=settings,
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.PERCENTAGE_OF_TOTAL_PRICE,
            percentage_of_total_price=50,
            to_be_paid_time_amount=1,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.WEEKS,
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_START_OF_EVENT,
        )
        expected_conditions = {
            datetime(
                2023,
                12,
                25,
                10,
                0,
                tzinfo=UTC,
            ): "50.00% of total price to be paid 1 weeks before the start of the event",
            datetime(
                2023,
                12,
                30,
                10,
                0,
                tzinfo=UTC,
            ): "Full price to be paid 2 days before the start of the event",
        }
        assert settings.get_conditions(event_reservation) == expected_conditions

    def test_get_example_event_reservation(self):
        organization = organization_factories.OrganizationFactory()
        settings = payment_factories.EventReservationPaymentSettingsFactory(
            organization=organization,
        )
        event = event_factories.SingleEventFactory(
            starting_at=timezone.make_aware(datetime(2024, 1, 1, 10, 0, 0)),
            ending_on=timezone.make_aware(datetime(2024, 1, 1, 12, 0, 0)),
            concept__organizer=organization,
        )
        event_reservation = reservation_factories.EventReservationFactory(
            event=event,
            organization=organization,
        )
        assert settings.get_example_event_reservation() == event_reservation

    def test_get_example_event_reservation_no_reservation(self):
        organization = organization_factories.OrganizationFactory()
        settings = payment_factories.EventReservationPaymentSettingsFactory(
            organization=organization,
        )
        assert settings.get_example_event_reservation() is None


@pytest.mark.django_db
class TestEventReservationPaymentCondition:
    def test_str_full_price(self):
        condition = payment_factories.EventReservationPaymentConditionFactory(
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.FULL_PRICE,
            to_be_paid_time_amount=2,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.DAYS,
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_START_OF_EVENT,
        )
        assert (
            str(condition)
            == "Full price to be paid 2 days before the start of the event"
        )

    def test_str_percentage(self):
        condition = payment_factories.EventReservationPaymentConditionFactory(
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.PERCENTAGE_OF_TOTAL_PRICE,
            percentage_of_total_price=50,
            to_be_paid_time_amount=1,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.WEEKS,
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_START_OF_EVENT,
        )
        assert (
            str(condition)
            == "50% of total price to be paid 1 weeks before the start of the event"
        )

    def test_str_fixed_price(self):
        condition = payment_factories.EventReservationPaymentConditionFactory(
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.FIXED_PRICE,
            to_be_paid_time_amount=3,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.HOURS,
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_START_OF_EVENT,
        )
        payment_factories.PriceFactory(
            vat_included=Money(10, EUR),
            unique_origin=condition,
        )
        assert (
            str(condition)
            == "Fixed price to be paid 3 hours before the start of the event"
        )

    def test_str_with_group_exceeds(self):
        condition = payment_factories.EventReservationPaymentConditionFactory(
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.FULL_PRICE,
            to_be_paid_time_amount=2,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.DAYS,
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_START_OF_EVENT,
            only_when_group_exceeds=10,
        )
        assert (
            str(condition)
            == "Full price to be paid 2 days before the start of the event but only when group exceeds 10 persons"  # noqa: E501
        )

    def test_get_due_date_at_start(self):
        event = event_factories.SingleEventFactory(
            starting_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            ending_on=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        )
        event_reservation = reservation_factories.EventReservationFactory(event=event)
        condition = payment_factories.EventReservationPaymentConditionFactory(
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.AT_START_OF_EVENT,
        )
        assert condition.get_due_date(event_reservation) == datetime(
            2024,
            1,
            1,
            10,
            0,
            0,
            tzinfo=UTC,
        )

    def test_get_due_date_at_end(self):
        event = event_factories.SingleEventFactory(
            starting_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            ending_on=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        )
        event_reservation = reservation_factories.EventReservationFactory(event=event)
        condition = payment_factories.EventReservationPaymentConditionFactory(
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.AT_END_OF_EVENT,
        )
        assert condition.get_due_date(event_reservation) == datetime(
            2024,
            1,
            1,
            12,
            0,
            0,
            tzinfo=UTC,
        )

    def test_get_due_date_before_start(self):
        event = event_factories.SingleEventFactory(
            starting_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            ending_on=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        )
        event_reservation = reservation_factories.EventReservationFactory(event=event)
        condition = payment_factories.EventReservationPaymentConditionFactory(
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_START_OF_EVENT,
            to_be_paid_time_amount=2,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.DAYS,
        )
        assert condition.get_due_date(event_reservation) == datetime(
            2023,
            12,
            30,
            10,
            0,
            0,
            tzinfo=UTC,
        )

    def test_get_due_date_after_start(self):
        event = event_factories.SingleEventFactory(
            starting_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            ending_on=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        )
        event_reservation = reservation_factories.EventReservationFactory(event=event)
        condition = payment_factories.EventReservationPaymentConditionFactory(
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.AFTER_START_OF_EVENT,
            to_be_paid_time_amount=1,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.HOURS,
        )
        assert condition.get_due_date(event_reservation) == datetime(
            2024,
            1,
            1,
            11,
            0,
            0,
            tzinfo=UTC,
        )

    def test_get_due_date_before_end(self):
        event = event_factories.SingleEventFactory(
            starting_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            ending_on=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        )
        event_reservation = reservation_factories.EventReservationFactory(event=event)
        condition = payment_factories.EventReservationPaymentConditionFactory(
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.BEFORE_END_OF_EVENT,
            to_be_paid_time_amount=30,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.MINUTES,
        )
        assert condition.get_due_date(event_reservation) == datetime(
            2024,
            1,
            1,
            11,
            30,
            0,
            tzinfo=UTC,
        )

    def test_get_due_date_after_end(self):
        event = event_factories.SingleEventFactory(
            starting_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC),
            ending_on=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        )
        event_reservation = reservation_factories.EventReservationFactory(event=event)
        condition = payment_factories.EventReservationPaymentConditionFactory(
            payment_moment=payment_models.EventReservationPaymentCondition.PaymentMoment.AFTER_END_OF_EVENT,
            to_be_paid_time_amount=1,
            to_be_paid_interval=payment_models.EventReservationPaymentCondition.ToBePaidInterval.DAYS,
        )
        assert condition.get_due_date(event_reservation) == datetime(
            2024,
            1,
            2,
            12,
            0,
            0,
            tzinfo=UTC,
        )

    def test_get_due_date_no_event(self):
        event_reservation = reservation_factories.EventReservationFactory(event=None)
        condition = payment_factories.EventReservationPaymentConditionFactory()
        assert condition.get_due_date(event_reservation) is None

    def test_get_price_full_price(self):
        matrix = payment_factories.AgePriceMatrixFactory(name="brunch prijzen 2024")
        baby = payment_factories.AgePriceMatrixItemFactory(
            from_age=0,
            till_age=10,
            age_price_matrix_id=matrix.pk,
        )
        payment_factories.PriceFactory(vat_included=Money(10, EUR), unique_origin=baby)
        event = event_factories.SingleEventFactory()
        event_reservation = reservation_factories.EventReservationFactory(
            event_id=event.pk,
        )
        reservation_factories.ReservationLineFactory(
            reservation=event_reservation,
            amount=2,
            price_matrix_item_id=baby.pk,
        )

        condition = payment_factories.EventReservationPaymentConditionFactory(
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.FULL_PRICE,
            only_when_group_exceeds=1,
        )
        assert condition.get_price(event_reservation).vat_included == Money(20, EUR)

    def test_get_price_fixed_price(self):
        matrix = payment_factories.AgePriceMatrixFactory(name="brunch prijzen 2024")
        baby = payment_factories.AgePriceMatrixItemFactory(
            from_age=0,
            till_age=10,
            age_price_matrix_id=matrix.pk,
        )
        payment_factories.PriceFactory(vat_included=Money(10, EUR), unique_origin=baby)
        event = event_factories.SingleEventFactory()
        event_reservation = reservation_factories.EventReservationFactory(
            event_id=event.pk,
        )
        reservation_factories.ReservationLineFactory(
            reservation=event_reservation,
            amount=2,
            price_matrix_item_id=baby.pk,
        )
        condition = payment_factories.EventReservationPaymentConditionFactory(
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.FIXED_PRICE,
            only_when_group_exceeds=1,
        )
        payment_factories.PriceFactory(
            vat_included=Money(5, EUR),
            unique_origin=condition,
        )
        assert condition.get_price(event_reservation).vat_included == Money(5, EUR)

    def test_get_price_percentage(self):
        matrix = payment_factories.AgePriceMatrixFactory(name="brunch prijzen 2024")
        baby = payment_factories.AgePriceMatrixItemFactory(
            from_age=0,
            till_age=10,
            age_price_matrix_id=matrix.pk,
        )
        payment_factories.PriceFactory(vat_included=Money(10, EUR), unique_origin=baby)
        event = event_factories.SingleEventFactory()
        event_reservation = reservation_factories.EventReservationFactory(
            event_id=event.pk,
        )
        line = reservation_factories.ReservationLineFactory(
            reservation=event_reservation,
            amount=2,
            price_matrix_item_id=baby.pk,
        )
        payment_factories.PriceFactory(
            vat_included=Money(10, EUR),
            unique_origin=line,
        )
        condition = payment_factories.EventReservationPaymentConditionFactory(
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.PERCENTAGE_OF_TOTAL_PRICE,
            percentage_of_total_price=50,
            only_when_group_exceeds=1,
        )
        assert condition.get_price(event_reservation).vat_included == Money(10, EUR)

    def test_get_price_fixed_price_per_person(self):
        matrix = payment_factories.AgePriceMatrixFactory(name="brunch prijzen 2024")
        adults = payment_factories.AgePriceMatrixItemFactory(
            from_age=18,
            till_age=77,
            age_price_matrix_id=matrix.pk,
        )
        payment_factories.PriceFactory(
            vat_included=Money(10, EUR),
            unique_origin=adults,
        )
        event = event_factories.SingleEventFactory()
        event_reservation = reservation_factories.EventReservationFactory(
            event_id=event.pk,
        )
        line = reservation_factories.ReservationLineFactory(
            reservation=event_reservation,
            amount=3,
            price_matrix_item_id=adults.pk,
        )
        payment_factories.PriceFactory(
            vat_included=Money(10, EUR),
            unique_origin=line,
        )
        condition = payment_factories.EventReservationPaymentConditionFactory(
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.FIXED_PRICE_PER_PERSON,
            only_when_group_exceeds=1,
        )
        payment_factories.PriceFactory(
            vat_included=Money(5, EUR),
            unique_origin=condition,
        )
        assert condition.get_price(event_reservation).vat_included == Money(15, EUR)

    def test_get_price_remaining_price(self):
        payment_request = payment_factories.PaymentRequestFactory()
        matrix = payment_factories.AgePriceMatrixFactory(name="brunch prijzen 2024")
        adults = payment_factories.AgePriceMatrixItemFactory(
            from_age=18,
            till_age=77,
            age_price_matrix_id=matrix.pk,
        )
        payment_factories.PriceFactory(
            vat_included=Money(10, EUR),
            unique_origin=adults,
        )
        event = event_factories.SingleEventFactory()
        event_reservation = reservation_factories.EventReservationFactory(
            event_id=event.pk,
            payment_request_id=payment_request.pk,
        )
        line = reservation_factories.ReservationLineFactory(
            reservation=event_reservation,
            amount=2,
            price_matrix_item_id=adults.pk,
        )

        payment_factories.PriceFactory(
            vat_included=Money(10, EUR),
            unique_origin=line,
        )
        payment_factories.PriceFactory(
            vat_included=line.total_price.vat_included,
            unique_origin=payment_request,
        )
        payment_factories.PaymentFactory(
            payment_request=event_reservation.payment_request,
            paid_amount=Money(5, EUR),
        )
        condition = payment_factories.EventReservationPaymentConditionFactory(
            prepayment_type=payment_models.EventReservationPaymentCondition.PrepaymentType.REMAINING_PRICE,
            only_when_group_exceeds=1,
        )
        assert condition.get_price(event_reservation) == Money(15, EUR)


@pytest.mark.django_db
def test_price_recalculation_on_vat_line_save(faker):
    price = payment_models.Price.objects.create()
    payment_models.VATPriceLine.objects.create(
        price=price,
        input_price=Money(100, EUR),
        includes_vat=False,
        vat_percentage=21,
    )
    price.refresh_from_db()
    assert price.vat_included == Money(121, EUR)
    assert price.vat_excluded == Money(100, EUR)
    assert price.vat == Money(21, EUR)
