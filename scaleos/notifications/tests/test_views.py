# /opt/scaleos/scaleos/notifications/tests/test_views.py

import logging
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.http import Http404
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

    def test_notification_list_view_unauthenticated_no_key_raises_error(
        self,
        client,  # Use client
    ):
        """
        Test view raises error when no key and user is not authenticated.
        get_object_or_404 will raise ValueError if lookup value is None.
        """
        url = reverse("notifications:notification")
        # No login needed for anonymous user with client

        # The view logic for this case hits get_object_or_404(..., public_key=None).
        # Assuming no notification has public_key=None, this raises Http404.
        with pytest.raises(Http404):
            client.get(url)  # Use client.get()

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

    def test_notification_detail_not_exists(self, client, user):  # Use client
        """Test viewing a notification that does not exist."""
        invalid_key = uuid4()
        url = reverse(
            "notifications:notification",
            kwargs={"notification_public_key": invalid_key},
        )

        client.force_login(user)  # Login user

        # The view uses get_object_or_404, which raises Http404
        with pytest.raises(Http404):
            client.get(url)  # Use client.get() inside the context manager

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
        assert isinstance(response, HttpResponseRedirect)
        # Or check response.status_code == 302
        assert response.status_code == 302
        assert response.url == redirect_target
        assert notification.seen_on is not None
        session = client.session
        assert session.get("active_organization_id") == org.pk

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

    def test_notification_without_sending_organization(
        self,  # Use client
        client,
        user,
        mock_get_templated_mail,
    ):
        """Test edge case where notification lacks a sending_organization."""
        notification = notification_factories.UserNotificationFactory.create(
            sending_organization=None,  # Explicitly None
            to_user=user,
            seen_on=None,
            redirect_url="",
        )
        url = reverse(
            "notifications:notification",
            kwargs={"notification_public_key": notification.public_key},
        )

        client.force_login(user)  # Login user

        # The view attempts request.session[".."] = notification.sending_organization.pk
        # which will raise AttributeError when sending_organization is None
        with pytest.raises(AttributeError):
            client.get(url)  # Use client.get() inside context manager


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

    def test_unsubscribe_view_not_exists(self, client, user):  # Use client
        """Test unsubscribe page for a notification that does not exist."""
        invalid_key = uuid4()
        url = reverse(
            "notifications:unsubscribe",
            kwargs={"notification_public_key": invalid_key},
        )

        client.force_login(user)  # Login user

        # View uses get_object_or_404
        with pytest.raises(Http404):
            client.get(url)  # Use client.get() inside context manager

    def test_unsubscribe_view_no_sending_org(self, client, user):  # Use client
        """Test unsubscribe page when notification has no sending_organization."""
        notification = notification_factories.UserNotificationFactory.create(
            sending_organization=None,  # Explicitly None
            to_user=user,
        )
        url = reverse(
            "notifications:unsubscribe",
            kwargs={"notification_public_key": notification.public_key},
        )

        client.force_login(user)  # Login user

        # View attempts request.session["..."] = notification.sending_organization.pk
        with pytest.raises(AttributeError):
            client.get(url)  # Use client.get() inside context manager
