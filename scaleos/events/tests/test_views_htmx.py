import pytest
from django.urls import reverse

from scaleos.events.tests import model_factories as event_factories


@pytest.mark.django_db
def test_htmx_concept(client):
    concept = event_factories.ConceptFactory()
    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "events_htmx:concept",
        kwargs={"concept_public_key": concept.public_key},
    )
    response = client.get(url, **headers)
    assert response.status_code == 200
