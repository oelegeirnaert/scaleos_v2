from unittest.mock import patch

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.cache import cache
from faker import Faker
from webpush.models import PushInformation
from webpush.models import SubscriptionInfo

from scaleos.users.models import User
from scaleos.users.tests.model_factories import UserFactory

faker = Faker()


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture(autouse=True)
def celery_eager(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture(autouse=True)
def patch_webpush_context():
    with patch("webpush.utils.get_templatetag_context", return_value={}):
        yield


@pytest.fixture
def verified_user(db):
    User = get_user_model()  # noqa: N806
    email = faker.email(domain="hotmail.com")
    password = faker.password()

    # Create user
    user = User.objects.create_user(
        email=email,
        password=password,
    )

    # Mark email as verified
    EmailAddress.objects.create(
        user=user,
        email=email,
        verified=True,
        primary=True,
    )

    user.raw_password = password  # optional, in case you need to log in
    return user


@pytest.fixture
def subscription():
    return SubscriptionInfo.objects.create(
        browser="Chrome",
        user_agent="Mozilla/5.0",
        endpoint="https://example.com/endpoint",
        auth="auth_key",
        p256dh="p256dh_key",
    )


@pytest.fixture
def webpush_user(user, subscription):
    return PushInformation.objects.create(
        user=user,
        subscription=subscription,
    )


@pytest.fixture
def clear_redis_cache():
    cache.clear()
