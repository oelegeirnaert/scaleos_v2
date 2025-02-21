import pytest
from django.urls import reverse

from scaleos.reservations.tests import model_factories as test_factories


@pytest.mark.django_db
def test_reservation_has_a_page(client):
    # inspired by: https://djangostars.com/blog/django-pytest-testing/

    reservation_public_key = "7534ecdb-3183-4b39-8f84-990261322c51"
    reservation = test_factories.ReservationFactory(public_key=reservation_public_key)
    assert reservation.html_public_key == "htmlPK7534ecdb31834b398f84990261322c51"
    url = reverse(
        "reservations:reservation",
        kwargs={"reservation_public_key": reservation_public_key},
    )
    response = client.get(url)
    assert response.status_code == 200

    non_existing_reservation_public_key = "7534ecdb-3183-4b39-8f84-990261322c52"
    url = reverse(
        "reservations:reservation",
        kwargs={"reservation_public_key": non_existing_reservation_public_key},
    )
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_event_reservation_has_a_page(client):
    # inspired by: https://djangostars.com/blog/django-pytest-testing/

    event_reservation_public_key = "7534ecdb-3183-4b39-8f84-990261322c51"
    event_reservation = test_factories.EventReservationFactory(
        public_key=event_reservation_public_key,
    )
    assert event_reservation.html_public_key == "htmlPK7534ecdb31834b398f84990261322c51"
    url = reverse(
        "reservations:eventreservation",
        kwargs={"eventreservation_public_key": event_reservation_public_key},
    )
    response = client.get(url)
    assert response.status_code == 200

    non_existing_reservation_public_key = "7534ecdb-3183-4b39-8f84-990261322c52"
    url = reverse(
        "reservations:eventreservation",
        kwargs={"eventreservation_public_key": non_existing_reservation_public_key},
    )
    response = client.get(url)
    assert response.status_code == 404
