import pytest

from scaleos.geography.tests import model_factories as geography_factories
from scaleos.users.tests import model_factories as user_factories


@pytest.mark.django_db
def test_set_gps_point_from_address(faker):
    address = geography_factories.AddressFactory(
        street="Molenstraat",
        house_number="36",
        postal_code="",
        city="",
    )
    assert not address.set_gps_point_from_address(), (
        "because we dont have a full address"
    )

    address = geography_factories.AddressFactory(
        street="Molenstraat",
        house_number="36",
        postal_code="1760",
        city="Pamel",
        country="BE",
    )
    assert str(address) == "Molenstraat 36, 1760 Pamel Belgium"
    assert address.set_gps_point_from_address()
    assert address.gps_point

    assert not address.set_gps_point_from_address(), "because it is not changed"


@pytest.mark.django_db
def test_get_full_address(faker):
    address = geography_factories.AddressFactory(
        street="Molenstraat",
        house_number="36",
        bus="A",
        postal_code="1760",
        city="Pamel",
        country="BE",
    )
    assert str(address) == "Molenstraat 36 A, 1760 Pamel Belgium"
    assert (
        address.get_full_address(with_country=False) == "Molenstraat 36 A, 1760 Pamel"
    )


@pytest.mark.django_db
def test_address_needs_correction(faker):
    """Because we have a house number in the street"""
    address = geography_factories.AddressFactory(
        street="Molenstraat 36",
        house_number="",
        postal_code="1760",
        city="Pamel",
        country="BE",
    )

    assert str(address) == "Molenstraat 36, 1760 Pamel"

    assert address.get_full_address(with_country=False) == "Molenstraat 36, 1760 Pamel"
    assert len(address.house_number) == 0
    assert address.needs_correction

    address.street = ("Molenstraat",)
    address.house_number = "36"
    user = user_factories.UserFactory()
    address.modified_by_id = user.id
    address.save()

    assert not address.needs_correction
