from urllib.parse import urlencode

import pytest
from django.core import mail
from django.urls import reverse

from scaleos.events.tests import model_factories as event_factories
from scaleos.payments.tests import model_factories as payment_factories
from scaleos.reservations import models as reservation_models
from scaleos.reservations.tests import model_factories as reservation_factories
from scaleos.users.tests import model_factories as user_factories


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
    a_reservation = reservation_factories.ReservationFactory(public_key=a_uuid)
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
    assert not a_reservation.requester_confirmed


@pytest.mark.django_db
def test_htmx_finish_reservation_reservation_is_successfull_as_authenticated(client):
    a_uuid = "c221ac76-3829-4e3d-975a-3504e3332ccc"
    to_email = "my_email@hotmail.com"
    a_password = "slen)3ij2"  # noqa: S105
    user = user_factories.UserFactory(email=to_email, password=a_password)
    reservation_factories.ReservationFactory(
        user_id=user.pk,
        public_key=a_uuid,
    )
    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "reservations_htmx:finish_reservation",
        kwargs={"reservation_public_key": a_uuid},
    )
    data = urlencode({"confirmation_email_address": to_email})
    client.login(username=to_email, password=a_password)
    response = client.post(
        url,
        data,
        content_type="application/x-www-form-urlencoded",
        **headers,
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_htmx_event_reservation_without_pricing(client):
    a_uuid = "c221ac76-3829-4e3d-975a-3504e3332ccc"
    event_factories.EventFactory(public_key=a_uuid)
    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "reservations_htmx:event_reservation",
        kwargs={"event_public_key": a_uuid},
    )
    response = client.get(url, **headers)
    assert response.status_code == 200


@pytest.mark.django_db
def test_htmx_event_reservation_with_pricing(client):
    age_price_matrix = payment_factories.AgePriceMatrixFactory()
    payment_factories.AgePriceMatrixItemFactory(
        age_price_matrix_id=age_price_matrix.pk,
    )
    concept = event_factories.ConceptFactory()
    event_factories.ConceptPriceMatrixFactory(
        concept_id=concept.pk,
        price_matrix_id=age_price_matrix.pk,
    )

    a_uuid = "c221ac76-3829-4e3d-975a-3504e3332ccc"
    event_factories.EventFactory(public_key=a_uuid, concept_id=concept.pk)
    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "reservations_htmx:event_reservation",
        kwargs={"event_public_key": a_uuid},
    )
    response = client.get(url, **headers)
    assert response.status_code == 200


@pytest.mark.django_db
def test_htmx_event_reservation_total_price(client):
    a_uuid = "c221ac76-3829-4e3d-975a-3504e3332bdd"
    reservation_factories.EventReservationFactory(public_key=a_uuid)
    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "reservations_htmx:event_reservation_total_price",
        kwargs={"eventreservation_public_key": a_uuid},
    )
    response = client.get(url, **headers)
    assert response.status_code == 200


@pytest.mark.django_db
def test_htmx_update_reservation_line(client):
    reservation_line_uuid = "c221ac76-3829-4e3d-975a-3504e5332bdd"

    event = event_factories.EventFactory.create()
    event_reservation = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        public_key=reservation_line_uuid,
        reservation_id=event_reservation.pk,
    )

    # First, access the session
    session = client.session
    session["event_reservation_id"] = event_reservation.pk
    session.save()  # Save the session

    headers = {"HTTP_HX-Request": "true"}
    data = {"amount": ""}
    url = reverse(
        "reservations_htmx:update_reservation_line",
        kwargs={"reservationline_public_key": reservation_line.public_key},
    )
    response = client.post(url, data, **headers)
    assert response.status_code == 200
    reservation_line.refresh_from_db()
    assert reservation_line.amount == 0


@pytest.mark.django_db
def test_htmx_update_reservation_line_with_two(client):
    reservation_line_uuid = "c221ac76-3829-4e3d-975a-3504e5332bdd"

    event = event_factories.EventFactory.create()
    event_reservation = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        public_key=reservation_line_uuid,
        reservation_id=event_reservation.pk,
    )

    # First, access the session
    session = client.session
    session["event_reservation_id"] = event_reservation.pk
    session.save()  # Save the session

    headers = {"HTTP_HX-Request": "true"}
    data = {"amount": 2}
    url = reverse(
        "reservations_htmx:update_reservation_line",
        kwargs={"reservationline_public_key": reservation_line.public_key},
    )
    response = client.post(url, data, **headers)
    assert response.status_code == 200
    reservation_line.refresh_from_db()
    assert reservation_line.amount == 2


@pytest.mark.django_db
def test_htmx_update_reservation_line_with_negative_amount(client):
    reservation_line_uuid = "c221ac76-3829-4e3d-975a-3504e5332bdd"

    event = event_factories.EventFactory.create()
    event_reservation = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        public_key=reservation_line_uuid,
        reservation_id=event_reservation.pk,
    )

    # First, access the session
    session = client.session
    session["event_reservation_id"] = event_reservation.pk
    session.save()  # Save the session

    headers = {"HTTP_HX-Request": "true"}
    data = {"amount": -4}
    url = reverse(
        "reservations_htmx:update_reservation_line",
        kwargs={"reservationline_public_key": reservation_line.public_key},
    )
    response = client.post(url, data, **headers)
    assert response.status_code == 200
    reservation_line.refresh_from_db()
    assert reservation_line.amount == 0


@pytest.mark.django_db
def test_htmx_update_reservation_line_with_real_text_amount(client):
    reservation_line_uuid = "c221ac76-3829-4e3d-975a-3504e5332bdd"

    event = event_factories.EventFactory.create()
    event_reservation = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        public_key=reservation_line_uuid,
        reservation_id=event_reservation.pk,
    )

    # First, access the session
    session = client.session
    session["event_reservation_id"] = event_reservation.pk
    session.save()  # Save the session

    headers = {"HTTP_HX-Request": "true"}
    data = {"amount": "i am text"}
    url = reverse(
        "reservations_htmx:update_reservation_line",
        kwargs={"reservationline_public_key": reservation_line.public_key},
    )
    response = client.post(url, data, **headers)
    assert response.status_code == 200
    reservation_line.refresh_from_db()
    assert reservation_line.amount == 0


@pytest.mark.django_db
def test_htmx_confirm_reservation(client):
    reservation = reservation_factories.ReservationFactory()

    headers = {"HTTP_HX-Request": "true"}
    url = reverse(
        "reservations_htmx:confirm_reservation",
    )
    data = {"reservation_public_key": reservation.public_key}
    response = client.post(url, data, **headers)
    assert response.status_code == 200
