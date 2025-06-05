# /opt/scaleos/scaleos/notifications/tests/test_views.py

import logging
from unittest.mock import MagicMock
from unittest.mock import patch
from urllib.parse import urlparse

import pytest
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from scaleos.notifications.tests import model_factories as notification_factories
from scaleos.organizations.tests import model_factories as organization_factories

# Assuming ITS_NOW is accessible or mock it if needed
from scaleos.users.tests.model_factories import UserFactory

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_get_templated_mail():
    """Mocks the get_templated_mail function."""
    mock_email = MagicMock()
    mock_email.subject = "Mock Subject"
    mock_email.body = "Mock Plain Body"
    mock_email.alternatives = [("Mock HTML Body", "text/html")]
    # Patch the location where the view imports it from
    with patch(
        "scaleos.notifications.views.get_templated_mail",
        return_value=mock_email,
    ) as mock:
        yield mock


class TestNotificationView:
    # Already converted
    def test_notification_list_view_authenticated_no_key(self, client, user):
        """
        Test the view when no public_key is provided and user is authenticated,
        using the test client to ensure URL resolution and full request lifecycle.
        """
        client.force_login(user)
        url = reverse("notifications:notification")
        response = client.get(url)

        assert response.status_code == 200
        assert "detail_list.html" in [t.name for t in response.templates]
        assert "details" in response.context
        assert not response.context["details"].exists()
        assert "app_name" in response.context
        assert "view_name" in response.context
        assert response.context["app_name"] == "notifications"
        assert response.context["view_name"] == "notification"

    def test_notification_detail_exists_authenticated(
        self,
        client,  # Use client
        user,
        mock_get_templated_mail,
    ):
        """Test viewing an existing notification detail page."""
        org = organization_factories.OrganizationFactory.create()
        notification = notification_factories.UserNotificationFactory.create(
            sending_organization=org,
            to_user=user,
            seen_on=None,
            redirect_url="",
        )
        url = reverse(
            "notifications:notification",
            kwargs={"notification_public_key": notification.public_key},
        )

        client.force_login(user)  # Login user
        response = client.get(url)  # Use client.get()
        notification.refresh_from_db()

        assert response.status_code == 200
        assert notification.page_template in [
            t.name for t in response.templates
        ]  # Check template
        assert "notification" in response.context  # Check context
        assert response.context["notification"] == notification
        assert notification.seen_on is not None
        # Check session via client.session after the request
        session = client.session
        assert session.get("active_organization_id") == org.pk
        assert "plain_body" in response.context
        assert "html_body" in response.context
        assert "email_subject" in response.context
        mock_get_templated_mail.assert_called_once()

    def test_notification_detail_exists_unauthenticated(
        self,  # Use client
        client,
        mock_get_templated_mail,
    ):
        """Test viewing an existing notification detail page when unauthenticated."""
        org = organization_factories.OrganizationFactory.create()
        user_for_notification = UserFactory()
        notification = notification_factories.UserNotificationFactory.create(
            sending_organization=org,
            to_user=user_for_notification,
            seen_on=None,
            redirect_url="",
        )
        url = reverse(
            "notifications:notification",
            kwargs={"notification_public_key": notification.public_key},
        )

        # No login needed for anonymous user
        response = client.get(url)  # Use client.get()
        notification.refresh_from_db()

        assert response.status_code == 200
        assert notification.page_template in [
            t.name for t in response.templates
        ]  # Check template
        assert "notification" in response.context  # Check context
        assert response.context["notification"] == notification
        assert notification.seen_on is not None
        session = client.session
        assert session.get("active_organization_id") == org.pk
        mock_get_templated_mail.assert_called_once()

    def test_notification_detail_redirects(self, client, user):  # Use client
        """Test that the view redirects if notification.redirect_url is set."""
        redirect_target = "/some/other/page/"
        org = organization_factories.OrganizationFactory.create()
        notification = notification_factories.UserNotificationFactory.create(
            sending_organization=org,
            to_user=user,
            seen_on=None,
            redirect_url=redirect_target,
        )
        url = reverse(
            "notifications:notification",
            kwargs={"notification_public_key": notification.public_key},
        )

        client.force_login(user)  # Login user
        response = client.get(url)  # Use client.get()
        notification.refresh_from_db()

        # Assertions for redirect remain the same
        assert isinstance(response, HttpResponseRedirect), (
            "the response should be a redirect"
        )
        # Or check response.status_code == 302
        assert response.status_code == 302, "the statuscode should be a 302"
        parsed_url = urlparse(response.url)
        path_only = parsed_url.path
        assert path_only == redirect_target, "the url should be the redirect url"
        assert notification.seen_on is not None, (
            "the notification should be marked as seen"
        )
        session = client.session
        assert session.get("active_organization_id") == org.pk, (
            "the session should be updated"
        )

    def test_notification_detail_seen_on_already_set(
        self,  # Use client
        client,
        user,
        mock_get_templated_mail,
    ):
        """Test that seen_on is not updated if already set."""
        past_time = timezone.now() - timezone.timedelta(days=1)
        org = organization_factories.OrganizationFactory.create()
        notification = notification_factories.UserNotificationFactory.create(
            sending_organization=org,
            to_user=user,
            seen_on=past_time,  # Already seen
            redirect_url="",
        )
        url = reverse(
            "notifications:notification",
            kwargs={"notification_public_key": notification.public_key},
        )

        client.force_login(user)  # Login user
        response = client.get(url)  # Use client.get()
        notification.refresh_from_db()

        assert response.status_code == 200
        assert notification.seen_on == past_time  # Should not have changed
        session = client.session
        assert session.get("active_organization_id") == org.pk
        mock_get_templated_mail.assert_called_once()


class TestNotificationSettingsView:
    def test_settings_view_authenticated(self, client, user):  # Use client
        """Test accessing settings page when logged in."""
        settings = notification_factories.UserNotificationSettingsFactory(user=user)
        url = reverse("notifications:notificationsettings")

        client.force_login(user)  # Login user
        response = client.get(url)  # Use client.get()

        assert response.status_code == 200
        assert settings.page_template in [
            t.name for t in response.templates
        ]  # Check template
        assert "notification_settings" in response.context  # Check context
        assert response.context["notification_settings"] == settings

    def test_settings_view_unauthenticated(self, client):  # Use client
        """Test accessing settings page when not logged in (should redirect)."""
        url = reverse("notifications:notificationsettings")

        # No login needed for anonymous user
        response = client.get(url)  # Use client.get()

        # @login_required decorator handles the redirect
        assert response.status_code == 302
        assert "login" in response.url  # Should redirect to login page


class TestUnsubscribeView:
    def test_unsubscribe_view_exists_authenticated(self, client, user):  # Use client
        """Test unsubscribe page for an existing notification (authenticated)."""
        org = organization_factories.OrganizationFactory.create()
        notification = notification_factories.UserNotificationFactory.create(
            sending_organization=org,
            to_user=user,
        )
        url = reverse(
            "notifications:unsubscribe",
            kwargs={"notification_public_key": notification.public_key},
        )

        client.force_login(user)  # Login user
        response = client.get(url)  # Use client.get()

        assert response.status_code == 200
        assert "notifications/notification/unsubscribe.html" in [
            t.name  # Check template
            for t in response.templates
        ]
        assert "notification" in response.context  # Check context
        assert response.context["notification"] == notification
        session = client.session
        assert session.get("active_organization_id") == org.pk

    def test_unsubscribe_view_exists_unauthenticated(self, client):  # Use client
        """Test unsubscribe page for an existing notification (unauthenticated)."""
        org = organization_factories.OrganizationFactory.create()
        user_for_notification = UserFactory()
        notification = notification_factories.UserNotificationFactory.create(
            sending_organization=org,
            to_user=user_for_notification,
        )
        url = reverse(
            "notifications:unsubscribe",
            kwargs={"notification_public_key": notification.public_key},
        )

        # No login needed for anonymous user
        response = client.get(url)  # Use client.get()

        assert response.status_code == 200
        assert "notifications/notification/unsubscribe.html" in [
            t.name  # Check template
            for t in response.templates
        ]
        assert "notification" in response.context  # Check context
        assert response.context["notification"] == notification
        session = client.session
        assert session.get("active_organization_id") == org.pk
