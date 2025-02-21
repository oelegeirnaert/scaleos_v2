import pytest
from django.utils.translation import activate
from moneyed import EUR
from moneyed import Money

from scaleos.payments.tests import model_factories as payment_factories


@pytest.mark.django_db
def test_price_format(faker):
    free = payment_factories.PriceFactory.create(current_price=None)
    assert free.text == "free"

    free_item = Money(0, EUR)
    free = payment_factories.PriceFactory.create(current_price=free_item)
    assert free.text == "free"

    two_euro = Money(2, EUR)
    price = payment_factories.PriceFactory.create(current_price=two_euro)
    assert str(price) == "€2.00"
    assert price.text == "€2.00"

    two_euro = Money(2.31, EUR)
    price = payment_factories.PriceFactory.create(current_price=two_euro)
    assert str(price) == "€2.31"
    assert price.text == "€2.31"

    activate("nl")
    assert price.text == "€2,31"


@pytest.mark.django_db
def test_price_vat_included(faker):
    price = payment_factories.PriceFactory.create(
        current_price=None,
        includes_vat=False,
        vat_percentage=21,
    )
    assert price.vat_included is None

    hundred_euro = Money(100, EUR)
    price = payment_factories.PriceFactory.create(
        current_price=hundred_euro,
        includes_vat=False,
        vat_percentage=21,
    )
    assert Money(121.00, "EUR") == price.vat_included

    hundred_euro = Money(100, EUR)
    price = payment_factories.PriceFactory.create(
        current_price=hundred_euro,
        includes_vat=True,
        vat_percentage=21,
    )
    assert Money(100, "EUR") == price.vat_included


@pytest.mark.django_db
def test_price_vat_excluded(faker):
    a_price = Money(106, EUR)
    price = payment_factories.PriceFactory.create(
        current_price=None,
        includes_vat=True,
        vat_percentage=6,
    )
    assert price.vat_excluded is None

    a_price = Money(106, EUR)
    price = payment_factories.PriceFactory.create(
        current_price=a_price,
        includes_vat=True,
        vat_percentage=6,
    )
    assert Money(99.64, "EUR") == price.vat_excluded

    a_price = Money(100, EUR)
    price = payment_factories.PriceFactory.create(
        current_price=a_price,
        includes_vat=False,
        vat_percentage=6,
    )
    assert Money(100, "EUR") == price.vat_excluded


@pytest.mark.django_db
def test_age_price_matrix_item_to_string(faker):
    matrix = payment_factories.AgePriceMatrixFactory(name="brunch prijzen 2024")
    baby = payment_factories.AgePriceMatrixItemFactory(
        from_age=0,
        till_age=10,
        age_price_matrix_id=matrix.pk,
    )
    assert str(baby) == "brunch prijzen 2024 (0-10): Free"

    price = payment_factories.PriceFactory(current_price=Money(10, EUR))
    grannies = payment_factories.AgePriceMatrixItemFactory(
        from_age=80,
        till_age=None,
        price_id=price.pk,
        age_price_matrix_id=matrix.pk,
    )
    activate("nl")
    assert str(grannies) == "brunch prijzen 2024 (80-...): €10,00"

    price = payment_factories.PriceFactory(current_price=Money(20, EUR))
    adults = payment_factories.AgePriceMatrixItemFactory(
        from_age=18,
        till_age=65,
        price_id=price.pk,
        age_price_matrix_id=matrix.pk,
    )
    activate("nl")
    assert str(adults) == "brunch prijzen 2024 (18-65): €20,00"
