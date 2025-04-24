from __future__ import annotations

import logging
import typing

from allauth.account import app_settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from scaleos.notifications.models import UserNotification
from scaleos.reservations.tasks import confirm_open_reservations_for_user
from scaleos.shared.mixins import ITS_NOW

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from scaleos.users.models import User
logger = logging.getLogger(__name__)


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    # Oele
    def confirm_email(self, request, email_address):
        user = email_address.user
        super().confirm_email(request, email_address)
        confirm_open_reservations_for_user.delay(user.pk)

        # Automatically log the user in after email confirmation
        if user.is_active:
            perform_login(request, user, email_verification="mandatory")

    # Oele
    def get_email_verification_redirect_url(self, email_address):
        """
        Redirect users to the password reset page after confirming their email.
        """
        return reverse(
            "custom_account_password_set",
        )  # Redirect to custom password set page

    def send_mail(self, template_prefix, email, context):
        logger.info("Custom send_mail is being used!")

    def send_email_confirmation(self, request, emailconfirmation, signup):
        logger.info("Custom send_email_confirmation is being used!")
        confirmation_url = self.get_email_confirmation_url(request, emailconfirmation)

        user_notification = UserNotification.objects.create(
            button_link=confirmation_url,
            to_user=emailconfirmation.email_address.user,
            about_content_object=emailconfirmation,
            title=_("email confirmation").title(),
        )
        user_notification.send()

    def send_password_reset_mail(self, user, email, context):
        """
        Override this to customize the password reset logic.
        You can send a custom email, trigger a webhook, etc.
        """
        # Logging or side effect
        logger.debug("[Password Reset] Requested by: %s", user.email)
        logger.debug("Context: %s", context)

        reset_url = context.get("password_reset_url", None)

        user_notification = UserNotification.objects.create(
            button_link=reset_url,
            button_text=_("reset password"),
            to_user=user,
            about_content_object=user,
            title=_("password reset").title(),
            message=_(
                "someone requested a password reset for your account",
            ).capitalize(),
        )
        user_notification.send()

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        ctx = {
            "user": emailconfirmation.email_address.user,
        }

        activate_url = self.get_email_confirmation_url(
            request,
            emailconfirmation,
        )
        if app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            ctx.update({"code": emailconfirmation.key})
        else:
            ctx.update(
                {
                    "key": emailconfirmation.key,
                    "activate_url": activate_url,
                },
            )
        emailconfirmation.sent = ITS_NOW
        emailconfirmation.save(update_fields=["sent"])

        if signup:
            user_notification = UserNotification.objects.create(
                button_link=activate_url,
                button_text=_("sign up"),
                to_user=emailconfirmation.email_address.user,
                about_content_object=emailconfirmation,
                title=_("welcome").title(),
                message=_("please sign up").capitalize(),
            )
        else:
            user_notification = UserNotification.objects.create(
                button_link=activate_url,
                button_text=_("reset password"),
                to_user=emailconfirmation.email_address.user,
                about_content_object=emailconfirmation,
                title=_("confirm your email").title(),
                message=_("please confirm your email address").capitalize(),
            )

        user_notification.send()


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user
