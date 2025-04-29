from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from scaleos.notifications.tests import model_factories as notification_factories
from scaleos.organizations.tests import model_factories as organization_factories
from scaleos.reservations.tests import model_factories as reservation_factories
from scaleos.users.models import User
from scaleos.users.tests import model_factories as user_factories

pytestmark = pytest.mark.django_db


class TestUser:
    def test_set_first_and_family_name(self, faker):
        user = user_factories.UserFactory.create(email="joske@hotmail.com")
        assert user.person.first_name == ""
        assert user.person.family_name == ""
        user.set_first_and_family_name("joske", "vermeulen", overwrite_existing=False)
        assert user.person.first_name == "joske"
        assert user.person.family_name == "vermeulen"
        user.set_first_and_family_name("piet", "huysentruyt", overwrite_existing=True)
        assert user.person.first_name == "piet"
        assert user.person.family_name == "huysentruyt"
        user.set_first_and_family_name("luc", "trots", overwrite_existing=False)
        assert user.person.first_name == "piet"
        assert user.person.family_name == "huysentruyt"

    def test_person_is_created_when_user_is_created(self, faker):
        user = user_factories.User()
        user.save()
        assert user.person is not None

    def test_user_has_webpush(self, webpush_user):
        user = webpush_user.user
        assert user.has_webpush is True

    @pytest.mark.django_db
    def test_user_has_no_webpush(self):
        user = user_factories.UserFactory.create()
        assert user.has_webpush is False

    @patch("webpush.utils._send_notification")
    def test_user_has_notifications(self, mock_send_notification, webpush_user):
        mock_send_notification.return_value = MagicMock(status=200, success=True)
        organization = organization_factories.OrganizationFactory()
        notification_factories.UserNotificationFactory(
            to_user=webpush_user.user,
            sending_organization_id=organization.pk,
        )
        assert webpush_user.user.has_notifications

    def test_user_get_absolute_url(self, user: User):
        assert user.get_absolute_url() == f"/my/{user.pk}/"

    def test_user_has_organizations(self):
        user = user_factories.UserFactory.create()
        organization_factories.OrganizationOwnerFactory(person=user.person)
        assert user.has_organizations

    def test_user_has_reservations(self):
        user = user_factories.UserFactory.create()
        reservation_factories.ReservationFactory(user=user)
        assert user.has_reservations
