import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_person_created_on_user_creation():
    user = get_user_model().objects.create_user(
        email="testemail@example.com",
        password="pass123",  # noqa: S106
    )
    assert hasattr(user, "person")
