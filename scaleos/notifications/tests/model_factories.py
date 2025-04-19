from factory import SubFactory
from factory.django import DjangoModelFactory

from scaleos.notifications import models as notifciation_models
from scaleos.users.tests import model_factories as user_factories


class NotificationFactory(
    DjangoModelFactory[notifciation_models.Notification],
):
    class Meta:
        model = notifciation_models.Notification


class UserNotificationFactory(
    DjangoModelFactory[notifciation_models.UserNotification],
):
    to_user = SubFactory(user_factories.UserFactory)

    class Meta:
        model = notifciation_models.UserNotification


class OrganizationNotificationFactory(
    DjangoModelFactory[notifciation_models.OrganizationNotification],
):
    class Meta:
        model = notifciation_models.OrganizationNotification


class WebPushNotificationFactory(
    DjangoModelFactory[notifciation_models.WebPushNotification],
):
    user = SubFactory(user_factories.UserFactory)
    notification = SubFactory(NotificationFactory)

    class Meta:
        model = notifciation_models.WebPushNotification


class MailNotificationFactory(
    DjangoModelFactory[notifciation_models.MailNotification],
):
    user = SubFactory(user_factories.UserFactory)
    notification = SubFactory(NotificationFactory)

    class Meta:
        model = notifciation_models.MailNotification
        django_get_or_create = ("user", "notification")


class UserNotificationSettingsFactory(
    DjangoModelFactory[notifciation_models.UserNotificationSettings],
):
    user = SubFactory(user_factories.UserFactory)

    class Meta:
        model = notifciation_models.UserNotificationSettings
        django_get_or_create = ["user"]
