from urllib.parse import urlencode

import pytest
from django.core import mail
from django.urls import reverse

from scaleos.events.tests import model_factories as event_factories
from scaleos.reservations import models as reservation_models
from scaleos.reservations.tests import model_factories as reservation_factories


@pytest.mark.django_db
def test_htmx_finish_reservation_bad_email(client):
    reservation = reservation_factories.ReservationFactory()
    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "reservations_htmx:finish_reservation",
        kwargs={"reservation_public_key": reservation.public_key},
    )
    data = urlencode({"confirmation_email_address": "jkd"})
    response = client.post(
        url,
        data,
        content_type="application/x-www-form-urlencoded",
        **headers,
    )
    assert response.status_code == 200
    assert "this is not a valid email address" in str(response.content)


@pytest.mark.django_db
def test_htmx_finish_reservation_reservation_does_not_exist(client):
    a_uuid = "c221ac76-3829-4e3d-975a-3504e3332bad"
    reservation_models.Reservation.objects.filter(public_key=a_uuid).delete()
    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "reservations_htmx:finish_reservation",
        kwargs={"reservation_public_key": a_uuid},
    )
    data = urlencode({"confirmation_email_address": "my_email@hotmail.com"})
    response = client.post(
        url,
        data,
        content_type="application/x-www-form-urlencoded",
        **headers,
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_htmx_finish_reservation_reservation_is_successfull(client):
    assert len(mail.outbox) == 0
    a_uuid = "c221ac76-3829-4e3d-975a-3504e3332ccc"
    to_email = "my_email@hotmail.com"
    reservation_factories.ReservationFactory(public_key=a_uuid)
    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "reservations_htmx:finish_reservation",
        kwargs={"reservation_public_key": a_uuid},
    )
    data = urlencode({"confirmation_email_address": to_email})
    response = client.post(
        url,
        data,
        content_type="application/x-www-form-urlencoded",
        **headers,
    )
    assert response.status_code == 200
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [to_email]


@pytest.mark.django_db
def test_htmx_get_event_reservation(client):
    a_uuid = "c221ac76-3829-4e3d-975a-3504e3332ccc"
    event_factories.EventFactory(public_key=a_uuid)
    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "reservations_htmx:event_reservation",
        kwargs={"event_public_key": a_uuid},
    )
    response = client.get(url, **headers)
    assert response.status_code == 200
