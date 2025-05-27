import pytest
from django.urls import reverse

from scaleos.organizations.tests import model_factories as organization_factories


@pytest.mark.django_db
def test_organization_can_show_concepts(client):
    # inspired by: https://djangostars.com/blog/django-pytest-testing/
    from scaleos.events.tests.model_factories import ConceptFactory

    organization_slug = "waerboom"
    waerboom = organization_factories.OrganizationFactory(slug=organization_slug)
    ConceptFactory.create_batch(3, organizer_id=waerboom.pk)
    url = reverse(
        "organizations:concepts",
        kwargs={"organization_slug": organization_slug},
    )
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ogranization(client):
    organization_slug = "waerboom"
    organization_factories.OrganizationFactory(slug=organization_slug)
    url = reverse(
        "organizations:organization",
        kwargs={"organization_slug": organization_slug},
    )
    response = client.get(url)
    assert response.status_code == 200
