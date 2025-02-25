import pytest
from celery.result import EagerResult
from django.core import mail

from scaleos.reservations import tasks as reservation_tasks
from scaleos.reservations.tests import model_factories as reservation_factories
from scaleos.shared.mixins import ITS_NOW
from scaleos.users.tests import model_factories as user_factories

pytestmark = pytest.mark.django_db


def test_send_reservation_confirmation_reservation_does_not_exist(settings):
    """A basic test to execute the get_users_count Celery task."""
    assert len(mail.outbox) == 0

    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = reservation_tasks.send_reservation_confirmation.delay(
        reservation_id=-1,
    )
    assert isinstance(task_result, EagerResult)
    assert len(mail.outbox) == 0, "because no user set"


def test_send_reservation_confirmation_without_user(settings):
    """A basic test to execute the get_users_count Celery task."""
    assert len(mail.outbox) == 0
    reservation = reservation_factories.ReservationFactory.create()
    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = reservation_tasks.send_reservation_confirmation.delay(
        reservation_id=reservation.pk,
    )
    assert isinstance(task_result, EagerResult)
    assert len(mail.outbox) == 0, "because no user set"


def test_send_reservation_confirmation_already_sent(settings):
    """A basic test to execute the get_users_count Celery task."""
    user = user_factories.UserFactory.create()
    assert len(mail.outbox) == 0
    reservation = reservation_factories.ReservationFactory.create(
        user_id=user.pk,
        confirmation_mail_sent_on=ITS_NOW,
    )
    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = reservation_tasks.send_reservation_confirmation.delay(
        reservation_id=reservation.pk,
    )
    assert isinstance(task_result, EagerResult)
    assert len(mail.outbox) == 0, "because mail is already sent"


def test_send_reservation_confirmation_success(settings):
    """A basic test to execute the get_users_count Celery task."""
    user = user_factories.UserFactory.create(email="jan_janssens@hotmail.com")
    assert len(mail.outbox) == 0
    reservation = reservation_factories.ReservationFactory.create(user_id=user.pk)
    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = reservation_tasks.send_reservation_confirmation.delay(
        reservation_id=reservation.pk,
    )
    assert isinstance(task_result, EagerResult)
    assert task_result.result
    assert len(mail.outbox) == 1
