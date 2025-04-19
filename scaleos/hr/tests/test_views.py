from unittest.mock import patch

import pytest
from django.urls import reverse

from scaleos.users.tests import model_factories as user_factories


@pytest.mark.django_db
@patch("webpush.utils.get_templatetag_context", return_value={})
def test_view_person_with_profile(mock_context, client):
    user = user_factories.UserFactory.create()
    assert hasattr(user, "person")

    client.force_login(user)
    url = reverse(
        "hr:person",
    )
    response = client.get(url)
    assert response.status_code == 200
