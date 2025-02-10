from django.urls import resolve
from django.urls import reverse

from scaleos.users.models import User


def test_url_organization_concept(user: User):
    organization_slug = "waerboom"
    expected_path = f"/organization/{organization_slug}/concept/"
    assert (
        reverse(
            "organizations:concepts",
            kwargs={"organization_slug": organization_slug},
        )
        == expected_path
    )
    assert resolve(expected_path).view_name == "organizations:concepts"
