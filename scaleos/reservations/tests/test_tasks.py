from datetime import timedelta

import pytest
from celery.result import EagerResult
from django.core import mail
from django.utils import timezone

from scaleos.reservations import tasks as reservation_tasks
from scaleos.reservations.tests import model_factories as reservation_factories
from scaleos.users.tests.model_factories import UserFactory

pytestmark = pytest.mark.django_db


def test_send_reservation_update_notification(settings):
    assert len(mail.outbox) == 0
    reservation_update = reservation_factories.OrganizationConfirmFactory()
    task_result = reservation_tasks.send_reservation_update_notification.delay(
        reservation_update_id=reservation_update.pk,
    )
    assert isinstance(task_result, EagerResult)
    assert len(mail.outbox) == 1


def test_confirm_open_reservations_for_user(faker):
    user = UserFactory.create()
    reservation = reservation_factories.ReservationFactory.create(user=user)
    past_date = timezone.now() - timedelta(days=1)
    expired_reservation = reservation_factories.ReservationFactory.create(
        user=user,
        expired_on=past_date,
    )
    reservation_tasks.confirm_open_reservations_for_user.delay(user.pk)
    assert reservation.requester_confirmed
    assert expired_reservation.requester_confirmed is False
