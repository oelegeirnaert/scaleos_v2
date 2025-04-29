import pytest
from allauth.account.models import EmailAddress
from allauth.account.models import EmailConfirmation
from celery.result import EagerResult
from django.core import mail
from django.test import RequestFactory

from scaleos.users.tasks import create_confirmation_notification
from scaleos.users.tasks import get_users_count
from scaleos.users.tests.model_factories import UserFactory

pytestmark = pytest.mark.django_db


def test_user_count(settings):
    """A basic test to execute the get_users_count Celery task."""
    batch_size = 3
    UserFactory.create_batch(batch_size)
    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = get_users_count.delay()
    assert isinstance(task_result, EagerResult)
    assert task_result.result == batch_size


def test_create_confirmation_notification(settings, client, clear_redis_cache):
    assert len(mail.outbox) == 0

    factory = RequestFactory()
    request = factory.get("/")
    user = UserFactory.create(email="joske@hotmail.com")

    email_address, email_created = EmailAddress.objects.get_or_create(
        user=user,
        email=user.email,
        primary=True,
    )

    email_confirmation = EmailConfirmation.create(email_address)
    create_confirmation_notification(request, email_confirmation)
    assert len(mail.outbox) == 1
