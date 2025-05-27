import pytest

from scaleos.events.models import Event
from scaleos.events.tests.model_factories import EventFactory
from scaleos.geography.tests.model_factories import AddressFactory


@pytest.mark.django_db
def test_admin_link_mixin(faker):
    assert Event.class_name() == "event"
    assert "list" in Event.list_template()

    address = AddressFactory()
    assert address.verbose_name == "address"

    assert "href" in address.admin_edit_button
    assert address.page_button is None, "because it has no public key"

    event = EventFactory()
    assert event.public_key
    assert "href" in event.page_button
    assert "</i>" in event.icon
