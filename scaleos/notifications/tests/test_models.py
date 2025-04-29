import logging
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from django.core import mail

from scaleos.notifications import models as notification_models
from scaleos.notifications.tests import model_factories as notification_factories
from scaleos.organizations.tests import model_factories as organization_factories

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestUserNotification:
    @patch("webpush.utils._send_notification")
    def test_user_notification_should_create_webpush_notification(
        self,
        mock_send_notification,
        webpush_user,
    ):
        mock_send_notification.return_value = MagicMock(status=200, success=True)
        organization = organization_factories.OrganizationFactory.create()

        notification = notification_factories.UserNotificationFactory.create(
            title="hi",
            message="hello",
            sending_organization_id=organization.pk,
            to_user_id=webpush_user.user.pk,
        )

        assert notification_models.WebPushNotification.objects.filter(
            notification_id=notification.pk,
        ).exists()

    def test_user_notification_should_create_mail_notification(self, faker):
        organization = organization_factories.OrganizationFactory.create()
        assert len(mail.outbox) == 0
        notification = notification_factories.UserNotificationFactory.create(
            title="hi",
            message="hello",
            sending_organization_id=organization.pk,
        )

        assert notification_models.MailNotification.objects.filter(
            notification_id=notification.pk,
        ).exists()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [notification.to_user.email]
