import pytest
from celery.result import EagerResult
from django.core import mail

from scaleos.reservations import tasks as reservation_tasks
from scaleos.reservations.tests import model_factories as reservation_factories

pytestmark = pytest.mark.django_db


def test_send_reservation_update_notification(settings):
    assert len(mail.outbox) == 0
    reservation_update = reservation_factories.OrganizationConfirmFactory()
    task_result = reservation_tasks.send_reservation_update_notification.delay(
        reservation_update_id=reservation_update.pk,
    )
    assert isinstance(task_result, EagerResult)
    assert task_result.result
    assert len(mail.outbox) == 1
