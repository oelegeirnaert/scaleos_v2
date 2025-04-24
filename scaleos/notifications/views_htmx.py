import logging

from django.http import HttpResponse
from django.views.decorators.cache import never_cache

from scaleos.notifications.models import UserNotificationSettings
from scaleos.shared.mixins import ITS_NOW

logger = logging.getLogger("scaleos")


@never_cache
def disable(request, user_notification_settings_public_key):
    notification_settings = UserNotificationSettings.objects.get(
        public_key=user_notification_settings_public_key,
    )
    notification_settings.disabled_all_notifications_on = ITS_NOW
    notification_settings.save()
    return HttpResponse("OK")
