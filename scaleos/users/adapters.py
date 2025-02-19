from __future__ import annotations

import logging
import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.shortcuts import reverse

from scaleos.core.tasks import send_custom_templated_email

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

    def send_email_confirmation(self, request, emailconfirmation, signup):
        logger.info("Custom send_email_confirmation is being used!")
        send_custom_templated_email(self, request, emailconfirmation)


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
