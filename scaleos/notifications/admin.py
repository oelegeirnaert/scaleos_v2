from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from scaleos.notifications import models as notification_models
from scaleos.shared.admin import LogInfoAdminMixin
from scaleos.shared.admin import generic_fk_admin_link


class MailNotificationInlineAdmin(admin.StackedInline):
    model = notification_models.MailNotification
    extra = 0
    show_change_link = True


class WebPushNotificationInlineAdmin(admin.StackedInline):
    model = notification_models.WebPushNotification
    extra = 0
    show_change_link = True
    readonly_fields = ["user", "title", "message", "icon_url", "show_notification_url"]


class NotificationInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class UserNotificationInlineAdmin(StackedPolymorphicInline.Child):
        model = notification_models.UserNotification
        show_change_link = True
        readonly_fields = ["to_user"]
        inlines = [MailNotificationInlineAdmin, WebPushNotificationInlineAdmin]

    class OrganizationNotificationInlineAdmin(StackedPolymorphicInline.Child):
        model = notification_models.OrganizationNotification
        show_change_link = True
        readonly_fields = ["to"]

    model = notification_models.Notification
    child_inlines = (
        UserNotificationInlineAdmin,
        OrganizationNotificationInlineAdmin,
    )


@admin.register(notification_models.Notification)
class NotificationAdmin(
    PolymorphicInlineSupportMixin,
    PolymorphicParentModelAdmin,
):
    base_model = notification_models.Notification
    child_models = [
        notification_models.Notification,
        notification_models.UserNotification,
        notification_models.OrganizationNotification,
    ]
    list_filter = [PolymorphicChildModelFilter]
    autocomplete_fields = [*LogInfoAdminMixin.autocomplete_fields]
    inlines = [WebPushNotificationInlineAdmin, MailNotificationInlineAdmin]
    readonly_fields = [
        "delay_options",
        "celery_status",
        "celery_result",
        "public_key",
        "show_notification_url",
        "open_notification_url",
        "about_link",
        "redirect_to_link",
        *LogInfoAdminMixin.readonly_fields,
    ]
    search_fields = ["public_key"]
    list_display = ["__str__", "about_content_type", "redirect_url"]

    @admin.display(
        description=_("notification about"),
    )
    def about_link(self, obj):
        return generic_fk_admin_link(
            obj.about_content_object,
            obj.about_content_type,
            obj.about_object_id,
        )

    @admin.display(
        description=_("redirect to"),
    )
    def redirect_to_link(self, obj):
        return generic_fk_admin_link(
            obj.redirect_to_content_object,
            obj.redirect_to_content_type,
            obj.redirect_to_object_id,
        )


@admin.register(notification_models.UserNotification)
class UserNotificationAdmin(
    NotificationAdmin,
    PolymorphicChildModelAdmin,
    LogInfoAdminMixin,
):
    base_model = notification_models.UserNotification  # Explicitly set here!
    # define custom features here
    inlines = [WebPushNotificationInlineAdmin, MailNotificationInlineAdmin]


@admin.register(notification_models.OrganizationNotification)
class OrganizationNotificationAdmin(PolymorphicChildModelAdmin, LogInfoAdminMixin):
    base_model = notification_models.OrganizationNotification  # Explicitly set here!
    # define custom features here
    inlines = [WebPushNotificationInlineAdmin, MailNotificationInlineAdmin]


@admin.register(notification_models.UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    pass
