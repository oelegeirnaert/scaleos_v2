import pytest
from django.urls import reverse

from scaleos.events.tests import model_factories as event_factories


@pytest.mark.django_db
def test_view_event(client):
    event = event_factories.EventFactory()
    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "events:event",
        kwargs={"event_public_key": event.public_key},
    )
    response = client.get(url, **headers)
    assert response.status_code == 200
