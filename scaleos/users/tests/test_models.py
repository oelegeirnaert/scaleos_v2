import pytest

from scaleos.notifications.tests import model_factories as notification_factories
from scaleos.organizations.tests import model_factories as organization_factories
from scaleos.reservations.tests import model_factories as reservation_factories
from scaleos.users.models import User
from scaleos.users.tests import model_factories as user_factories

pytestmark = pytest.mark.django_db


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/my/{user.pk}/"


def test_user_has_notifications(faker):
    user = user_factories.UserFactory.create()
    notification_factories.UserNotificationFactory(to_user=user)
    assert user.has_notifications


def test_user_has_organizations(faker):
    user = user_factories.UserFactory.create()
    organization_factories.OrganizationOwnerFactory(person=user.person)
    assert user.has_organizations


def test_user_has_reservations(faker):
    user = user_factories.UserFactory.create()
    reservation_factories.ReservationFactory(user=user)
    assert user.has_reservations
