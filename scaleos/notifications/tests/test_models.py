import logging

import pytest
from django.core import mail

from scaleos.notifications import models as notification_models
from scaleos.notifications.tests import model_factories as notification_factories

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestUserNotification:
    def test_user_notification_should_create_webpush_notification(self, faker):
        notification = notification_factories.UserNotificationFactory.create(
            title="hi",
            message="hello",
        )

        assert notification_models.WebPushNotification.objects.filter(
            notification_id=notification.pk,
        ).exists()

    def test_user_notification_should_create_mail_notification(self, faker):
        assert len(mail.outbox) == 0
        notification = notification_factories.UserNotificationFactory.create(
            title="hi",
            message="hello",
        )

        assert notification_models.MailNotification.objects.filter(
            notification_id=notification.pk,
        ).exists()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [notification.to_user.email]
