import logging
import uuid
from enum import Enum

from allauth.account.models import EmailConfirmation
from celery.exceptions import NotRegistered
from celery.result import AsyncResult
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import ValidationError
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils import translation
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from kombu.exceptions import OperationalError
from polymorphic.models import PolymorphicModel
from templated_email import send_templated_mail
from webpush import send_user_notification

from config import celery_app
from scaleos.notifications import tasks as notification_tasks
from scaleos.organizations import models as organization_models
from scaleos.organizations.functions import get_software_owner
from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.functions import get_base_url_from_string
from scaleos.shared.functions import is_blank
from scaleos.shared.mixins import ITS_NOW
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.users import models as user_models

logger = logging.getLogger(__name__)


# Create your models here.
class Notification(PolymorphicModel, LogInfoFields, AdminLinkMixin, PublicKeyField):
    class NotificationType(models.TextChoices):
        RESENGO_IMPORT_READY = "resengo_import_ready", _("Resengo import ready")
        ORGANIZATION_CONFIRMED_EVENT_RESERVATION = (
            "organization_confirmed_event_reservation",
            _("organization confirmed event reservation"),
        )

        UNKNOWN = "unknown", _("unknown")

    class NotificationResult(models.TextChoices):
        CREATED = "CREATED", _("created")
        SENT = "SENT", _("sent")
        DISMISSED = "DISMISSED", _("dismissed")
        MODIFIED = "MODIFIED", _("modified")
        READ = "READ", _("read")
        SEEN = "SEEN", _("seen")
        CONFIRMED = "CONFIRMED", _("confirmed")
        CANCELED = "CANCELED", _("canceled")
        COMPLETED = "COMPLETED", _("completed")
        ERROR = "error", _("error")
        SUCCESS = "SUCCESS", _("success")
        FAILED = "FAILED", _("failed")
        UNKNOWN = "UNKNOWN", _("unknown")

    class ToBeSendInterval(models.TextChoices):
        SECONDS = "seconds", _("seconds")
        MINUTES = "minutes", _("minutes")
        HOURS = "hours", _("hour")
        DAYS = "days", _("days")
        WEEKS = "weeks", _("weeks")
        MONTHS = "months", _("months")
        YEARS = "years", _("years")

    mail_template = "notification/notification.email"

    sending_organization = models.ForeignKey(
        organization_models.Organization,
        on_delete=models.CASCADE,
        null=True,
    )

    title = models.CharField(max_length=255, default="", blank=True)
    message = models.TextField(blank=True, default="")
    button_text = models.CharField(max_length=255, default="", blank=True)
    button_link = models.URLField(blank=True, default="")
    send_on = models.DateTimeField(null=True, blank=True)
    send_in_amount = models.IntegerField(default=0)
    send_in_interval = models.CharField(
        max_length=50,
        choices=ToBeSendInterval.choices,
        default=ToBeSendInterval.SECONDS,
    )
    sent_on = models.DateTimeField(verbose_name=_("sent on"), null=True, blank=True)
    seen_on = models.DateTimeField(null=True, blank=True)
    expires_on = models.DateTimeField(null=True, blank=True)
    dismissed_on = models.DateTimeField(null=True, blank=True)
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.UNKNOWN,
        blank=True,
    )

    about_content_type = models.ForeignKey(
        ContentType,
        related_name="about_notifications",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    about_object_id = models.PositiveIntegerField(null=True, blank=True)
    about_content_object = GenericForeignKey("about_content_type", "about_object_id")

    redirect_to_content_type = models.ForeignKey(
        ContentType,
        related_name="redirect_to_notifications",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    redirect_to_object_id = models.PositiveIntegerField(null=True, blank=True)
    redirect_to_content_object = GenericForeignKey(
        "redirect_to_content_type",
        "redirect_to_object_id",
    )
    redirect_url = models.URLField(default="", blank=True, max_length=300)
    result = models.CharField(
        max_length=50,
        choices=NotificationResult.choices,
        default=NotificationResult.UNKNOWN,
        blank=True,
    )

    celery_task_id = models.UUIDField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ["-created_on"]
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")

    def set_redirect_url(self):
        logger.setLevel(logging.DEBUG)
        logger.debug("Set redirect url")
        the_url = self.redirect_url
        if not is_blank(the_url):
            logger.debug("we already have a redirect url: %s", the_url)
            self.redirect_url = self.make_outgoing_link(self.redirect_url)
            return

        if self.redirect_to_content_object:
            redirect_url = self.get_redirect_url(self.redirect_to_content_object)
            if not is_blank(redirect_url):
                self.redirect_url = self.make_outgoing_link(redirect_url)
                return

        if self.about_content_object:
            redirect_url = self.get_redirect_url(self.about_content_object)
            if not is_blank(redirect_url):
                self.redirect_url = self.make_outgoing_link(redirect_url)
                return

    def get_redirect_url(self, a_field):
        logger.setLevel(logging.DEBUG)
        if a_field:
            try:
                app_label = a_field.app_label
                model_name = a_field.model_name
                the_kwarg = f"{model_name}_public_key"
                pk_field = "public_key"
                if not hasattr(a_field, pk_field):
                    msg = f"The model name {model_name} from app {app_label} has no attribute {pk_field}"  # noqa: E501
                    logger.warning(msg)
                    return None
                logger.debug(
                    "Trying to find the redirect: %s:%s with kwarg %s",
                    app_label,
                    model_name,
                    the_kwarg,
                )
                the_url = reverse(
                    f"{app_label}:{model_name}",
                    kwargs={the_kwarg: a_field.public_key},
                )
                logger.debug("Reverse match found: %s", the_url)

            except NoReverseMatch:
                logger.debug("no reverse match")
                return None
            except AttributeError:
                logger.debug("attribute error")
                return None
            else:
                return the_url
        logger.debug("no redirect url for %s", model_name)

        return None

    @property
    def unsubscribe_link(self):
        the_path = reverse(
            "notifications:unsubscribe",
            kwargs={"notification_public_key": self.public_key},
        )
        return f"{self.base_url}{the_path}"

    @property
    def send_in_amount_in_seconds(self):
        if not self.send_in_amount:
            return 0  # or None if you want to signal "not set"

        multiplier_map = {
            self.ToBeSendInterval.SECONDS: 1,
            self.ToBeSendInterval.MINUTES: 60,
            self.ToBeSendInterval.HOURS: 60 * 60,
            self.ToBeSendInterval.DAYS: 60 * 60 * 24,
            self.ToBeSendInterval.WEEKS: 60 * 60 * 24 * 7,
            self.ToBeSendInterval.MONTHS: 60 * 60 * 24 * 30,  # Approx: 30 days
            self.ToBeSendInterval.YEARS: 60 * 60 * 24 * 365,  # Approx: 365 days
        }

        multiplier = multiplier_map.get(self.send_in_interval, 1)
        return self.send_in_amount * multiplier

    @property
    def delay_options(self):
        if self.send_on:
            return {"eta": self.send_on}
        send_in_secs = self.send_in_amount_in_seconds
        if send_in_secs > 0:
            return {"countdown": self.send_in_amount_in_seconds}  # wait 5 seconds

        return {}  # should return an empty dict for apply_async

    @cached_property
    def first_allowed_host(self):
        return settings.ALLOWED_HOSTS[0]

    @property
    def base_url(self):
        logger.debug("Getting base url")
        try:
            if (
                self.sending_organization
                and hasattr(self.sending_organization, "internal_url")
                and not is_blank(self.sending_organization.internal_url)
            ):
                base_url = get_base_url_from_string(
                    self.sending_organization.internal_url,
                )
                logger.debug(base_url)
                return get_base_url_from_string(base_url)
        except KeyError:
            return f"https://{self.first_allowed_host}"
        else:
            return f"https://{self.first_allowed_host}"

    @cached_property
    def show_notification_url(self):
        relative_url = reverse(
            "notifications:notification",
            kwargs={"notification_public_key": self.public_key},
        )
        return f"{self.base_url}{relative_url}"

    @cached_property
    def open_notification_url(self):
        if self.public_key is None:
            self.public_key = uuid.uuid4()
        relative_url = reverse(
            "notifications:open_notification",
            kwargs={"notification_public_key": self.public_key},
        )
        return f"{self.base_url}{relative_url}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # True if this is a new object

        if hasattr(self, "language") and self.language:
            translation.activate(self.language)

        self.set_redirect_url()
        self.set_sending_organization()
        self.set_title()
        self.set_message()
        self.set_button_text()
        self.set_button_link()

        translation.deactivate()

        super().save(*args, **kwargs)

        if is_new:
            logger.debug("Trying to send notification %s", self.pk)
            if self.sent_on:
                logger.info(
                    "This notification has already been sent on %s",
                    self.sent_on,
                )
                return
            logger.debug("Prepare notification sending")

        notification_tasks.prepare_notification_sending.apply_async(
            (self.id,),
            **self.delay_options,
            task_id=str(self.public_key),
        )

    def clean(self):
        if self.send_in_amount > 0 and self.send_on:
            msg = _("please choose one of both options")
            raise ValidationError({"send_in_amount": msg, "send_on": msg})

        if self.about_content_object and self.redirect_url:
            msg = _("please choose one of both options")
            raise ValidationError({"about_content_object": msg, "redirect_url": msg})

    @property
    def celery_task_result(self):
        return AsyncResult(self.celery_task_id)

    @property
    def celery_status(self):
        return self.celery_task_result.status

    @property
    def celery_result(self):
        return self.celery_task_result.result

    def cancel_task(self):
        try:
            revoked = celery_app.control.revoke(self.celery_task_id, terminate=False)
            logger.info("Revoked Celery task: %s", {self.celery_task_id})

        except NotRegistered:
            logger.warning("Task with ID %s is not registered.", self.celery_task_id)
        except OperationalError:
            logger.exception(
                "Broker connection error while revoking task %s",
                self.celery_task_id,
            )
        except Exception:
            logger.exception(
                "Unexpected error while revoking task %s",
                self.celery_task_id,
            )
        else:
            return revoked

    def set_title(self):
        if not is_blank(self.title):
            return

        if hasattr(self, "notification"):
            if hasattr(self.notification, "title") and not is_blank(
                self.notification.title,
            ):
                self.title = self.notification.title
                return

        if hasattr(self, "about_content_object") and hasattr(
            self.about_content_object,
            "notification_title",
        ):
            self.title = self.about_content_object.notification_title
            return

        if hasattr(self, "about_content_object") and hasattr(
            self.about_content_object,
            "verbose_name",
        ):
            self.title = self.about_content_object.verbose_name.upper()
            return

    def set_message(self):
        if not is_blank(self.message):
            return

        if hasattr(self, "notification"):
            if hasattr(self.notification, "message") and not is_blank(
                self.notification.message,
            ):
                self.message = self.notification.message
                return

        if hasattr(self, "about_content_object") and hasattr(
            self.about_content_object,
            "notification_message",
        ):
            self.message = self.about_content_object.notification_message
            return

        if hasattr(self, "about_content_object") and hasattr(
            self.about_content_object,
            "verbose_name",
        ):
            self.message = str(self.about_content_object)
            return

    def set_button_text(self):
        if not is_blank(self.button_text):
            return

        if hasattr(self, "notification"):
            if hasattr(self.notification, "button_text") and not is_blank(
                self.notification.button_text,
            ):
                self.button_text = self.notification.button_text
                return

        if hasattr(self, "about_content_object") and hasattr(
            self.about_content_object,
            "notification_button_text",
        ):
            self.button_text = self.about_content_object.notification_button_text
            return

        translate_button_text = _("click here")
        self.button_text = translate_button_text

    def set_button_link(self):
        if not is_blank(self.button_link):
            return

        if hasattr(self, "open_notification_url"):
            self.button_link = self.open_notification_url
            return

        self.button_link = self.base_url

    def set_sending_organization(self):
        logger.debug("Set sending organization")
        if self.sending_organization:
            logger.debug("is already set")
            return

        the_owner = get_software_owner()
        if the_owner:
            logger.debug("The sending organization is the software owner.")
            self.sending_organization_id = the_owner.pk
            return

        logger.debug("We cannot set a sending organization")
        self.sending_organization = None

    def make_outgoing_link(self, link):
        if link is None:
            return None
        if not link.startswith("http://") or not link.startswith("https://"):
            return f"{self.base_url}{link}"
        return link


class UserNotification(Notification):
    class NotificationChannel(Enum):
        MAIL = "mail"
        WEBPUSH = "webpush"
        LETTER = "letter"
        VOICECALL = "voicecall"
        SMS = "sms"

    to_user = models.ForeignKey(
        user_models.User,
        verbose_name=_("to user"),
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
    )

    language = models.CharField(
        max_length=50,
        choices=settings.LANGUAGES,
        default="",
        blank=True,
    )

    def save(self, *args, **kwargs):
        if self.to_user:
            self.language = self.to_user.get_primary_language()
        return super().save(*args, **kwargs)

    def send_webpush(self, notification_settings, to_user_id):
        if not self.to_user.has_webpush:
            logger.info("The user has no webpush")
            return False

        if self.about_content_type:
            logger.info(self.about_content_type.model_class())
            if self.about_content_type.model_class() == EmailConfirmation:
                logger.warning("Never send a push when email needs to be confirmed")
                return False

        logger.debug("Trying to send a webpush notification")
        if notification_settings.disabled_webpush_notifications_on:
            logger.info(
                "The user disabled webpush notifications on %s",
                notification_settings.disabled_webpush_notifications_on,
            )
            return False

        if not hasattr(self, "webpush_notification"):
            WebPushNotification.objects.create(
                notification_id=self.pk,
                user_id=to_user_id,
            ).send()
            return True

        logger.info("Webpush already sent.")
        return False

    def send_mail(self, notification_settings, to_user_id):
        logger.debug("Trying to send a mail notification")
        if notification_settings.disabled_email_notifications_on:
            logger.info(
                "The user disabled email notifications on %s",
                notification_settings.disabled_email_notifications_on,
            )
        elif not hasattr(self, "mail_notification"):
            logger.debug(
                "Trying to create a mail notification for user %s",
                to_user_id,
            )
            MailNotification.objects.create(
                user_id=to_user_id,
                notification_id=self.pk,
            ).send()
        else:
            logger.info("Mail already sent.")

    def send(self):
        logger.debug("Send notification for user %s", self.pk)

        if self.to_user is None:
            logger.warning("we cannot send a user notification without a user")
            return False

        to_user_id = self.to_user.pk
        notification_settings, created = UserNotificationSettings.objects.get_or_create(
            user_id=to_user_id,
        )
        if created:
            logger.debug("New settings created for the user %s", to_user_id)

        if notification_settings.disabled_all_notifications_on:
            logger.info(
                "The user disabled all notifications on %s",
                notification_settings.disabled_all_notifications_on,
            )
            return False

        self.send_webpush(notification_settings, to_user_id)
        self.send_mail(notification_settings, to_user_id)
        return True


class OrganizationNotification(Notification):
    class NotificationTo(models.TextChoices):
        FULL_ORGANIZATION = "FULL_ORGANIZATION", _("full organization")
        ORGANIZATION_OWNERS = "ORGANIZATION_OWNERS", _("organization owners")
        ORGANIZATION_EMPLOYEES = "ORGANIZATION_EMPLOYEES", _("organization employees")
        ORGANIZATION_SUPPLIERS = "ORGANIZATION_SUPPLIERS", _("organization suppliers")
        ORGANIZATION_CUSTOMERS = "ORGANIZATION_CUSTOMERS", _("organization customers")

    to = models.CharField(
        max_length=50,
        choices=NotificationTo.choices,
        default="",
        blank=True,
    )


class WebPushNotification(LogInfoFields):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
        related_name="webpush_notification",
        null=True,
    )

    user = models.ForeignKey(
        user_models.User,
        on_delete=models.CASCADE,
        related_name="webpush_notifications",
    )

    title = models.CharField(max_length=255, default="", blank=True)
    message = models.TextField(blank=True, default="")
    icon_url = models.URLField(blank=True, default="")
    show_notification_url = models.URLField(blank=True, default="")

    def send(self):
        logger.debug("Trying to send a push notification to %s", self.user)

        notification_title = self.notification.title
        if is_blank(self.title) and notification_title is not None:
            self.title = notification_title
            self.save(update_fields=["title"])

        notification_message = self.notification.message
        if is_blank(self.message) and notification_message:
            self.message = notification_message
            self.save(update_fields=["message"])

        notification_redirect_url = self.notification.redirect_url
        if is_blank(self.show_notification_url):
            if notification_redirect_url is not None:
                self.show_notification_url = notification_redirect_url
            if self.notification and hasattr(
                self.notification,
                "show_notification_url",
            ):
                self.show_open_notification_url = (
                    self.notification.show_notification_url
                )
            self.save(update_fields=["show_notification_url"])

        if (
            is_blank(self.icon_url)
            and self.notification is not None
            and hasattr(self.notification, "sending_organization")
            and self.notification.sending_organization is not None
        ):
            if (
                self.notification.sending_organization.styling
                and self.notification.sending_organization.styling.fav_icon
            ):
                relative_icon_url = (
                    self.notification.sending_organization.styling.fav_icon.url
                )
                self.icon_url = f"{self.notification.base_url}{relative_icon_url}"

            if (
                self.notification.sending_organization.styling
                and self.notification.sending_organization.styling.logo
            ):
                relative_icon_url = (
                    self.notification.sending_organization.styling.logo.url
                )
                self.icon_url = f"{self.notification.base_url}{relative_icon_url}"

            self.save(update_fields=["icon_url"])

        payload = {
            "head": str(self.title),
            "body": str(self.message),
            "icon": str(self.icon_url),
            "url": str(self.show_notification_url),
        }
        logger.debug("Payload: %s", payload)
        ttl = 10227000
        if self.notification.expires_on:
            ttl = (self.notification.expires_on - ITS_NOW).total_seconds()
        send_user_notification(user=self.user, payload=payload, ttl=ttl)
        logger.info("Push notification sent")


class MailNotification(LogInfoFields):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
        related_name="mail_notification",
        null=True,
    )

    user = models.ForeignKey(
        user_models.User,
        on_delete=models.CASCADE,
        related_name="mail_notifications",
        null=True,
    )
    to_email_addresses = models.TextField(
        blank=False,
        default="",
        help_text=_("Use a comma ',' as the separator"),
    )
    cc_email_addresses = models.TextField(
        blank=True,
        default="",
        help_text=_("Use a comma ',' as the separator"),
    )
    bcc_email_addresses = models.TextField(
        blank=True,
        default="",
        help_text=_("Use a comma ',' as the separator"),
    )

    subject = models.CharField(max_length=255, default="", blank=True)
    body = models.TextField(blank=True, default="")
    html_body = models.TextField(blank=True, default="")

    def send(self):
        if is_blank(self.to_email_addresses):
            logger.debug("To addresses is empty")
            if self.user and self.user.email:
                logger.debug("Getting email from user")
                self.to_email_addresses = self.user.email

            elif hasattr(self, "to_user"):
                logger.debug("Getting email from TO-user")
                self.to_email_addresses = self.to_user.email

            self.save(update_fields=["to_email_addresses"])

        recipient_list = self.to_email_addresses.split(",")
        cc_list = self.cc_email_addresses.split(",")
        bcc_list = self.bcc_email_addresses.split(",")

        logger.debug("Trying to send a mail notification TO: %s", recipient_list)
        logger.debug("Trying to send a mail notification CC: %s", cc_list)
        logger.debug("Trying to send a mail notification BCC: %s", bcc_list)

        # https://pypi.org/project/django-templated-email/
        send_templated_mail(
            template_name=self.notification.mail_template,
            context={
                "notification": self.notification,
            },
            subject=self.subject,
            message=self.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            cc=cc_list,
            bcc=bcc_list,
            html_message=self.html_body,
        )
        logger.info("Mail notification sent.")


class UserNotificationSettings(AdminLinkMixin, LogInfoFields, PublicKeyField):
    user = models.OneToOneField(
        user_models.User,
        on_delete=models.CASCADE,
        related_name="notification_settings",
    )
    disabled_all_notifications_on = models.DateTimeField(null=True)
    disabled_webpush_notifications_on = models.DateTimeField(null=True)
    disabled_email_notifications_on = models.DateTimeField(null=True)

    webpush_only_during_working_hours = models.BooleanField(default=False)
    email_only_during_working_hours = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("user notification settings")
        verbose_name_plural = _("user notification settings")
