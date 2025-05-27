import pytest
from django.urls import reverse

from scaleos.payments.tests import model_factories as payment_factories


@pytest.mark.django_db
def test_admin_price_changelist(admin_client):
    url = reverse(
        "admin:payments_price_changelist",
    )
    response = admin_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_price_view(admin_client):
    price = payment_factories.PriceFactory.create()
    url = reverse(
        "admin:payments_price_change",
        kwargs={"object_id": price.pk},
    )
    response = admin_client.get(url)
    assert response.status_code == 200
