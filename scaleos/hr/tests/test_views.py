import pytest
from django.core.cache import cache
from django.urls import reverse

from scaleos.hr.tests import model_factories as hr_factories
from scaleos.users.tests import model_factories as user_factories


@pytest.mark.django_db
def test_view_person_with_profile(client):
    user = user_factories.UserFactory.create()
    hr_factories.PersonFactory.create(user_id=user.pk)

    assert hasattr(user, "person")

    client.force_login(user)
    url = reverse(
        "hr:person",
    )
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_person_without_profile(client):
    cache.clear()  # Clears all cached data
    user2 = user_factories.UserFactory.create(email="jeanke@hotmail.com")
    assert not hasattr(user2, "person")
    client.force_login(user2)
    url = reverse(
        "hr:person",
    )
    response = client.get(url)
    assert response.status_code == 200
