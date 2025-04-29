#!/usr/bin/env python
import logging
from typing import ClassVar

import pytz
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import EmailField
from django.db.models import ImageField
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from webpush.models import PushInformation

from scaleos.shared.mixins import AdminLinkMixin

from .managers import UserManager

logger = logging.getLogger(__name__)


class User(AbstractUser, AdminLinkMixin):
    """
    Default custom user model for ScaleOS.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    timezone = CharField(
        max_length=64,
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default="Europe/Brussels",
    )
    username = None  # type: ignore[assignment]
    website_language = CharField(
        verbose_name=_("website language"),
        max_length=50,
        choices=settings.LANGUAGES,
        default="",
        blank=True,
    )

    avatar = ImageField(upload_to="avatars", null=True, blank=True)
    avatar_thumbnail = ImageSpecField(
        source="avatar",
        processors=[ResizeToFill(50, 50)],
        format="JPEG",
        options={"quality": 60},
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

    @cached_property
    def has_organizations(self):
        if not hasattr(self, "person") or self.person is None:
            return False
        return self.person.owning_organizations.count() > 0

    @property
    def primary_telephone_number(self):
        if not hasattr(self, "person"):
            return None
        return self.person.primary_telephone_number

    @cached_property
    def is_email_verified(self):
        return EmailAddress.objects.filter(user=self, verified=True).exists()

    @property
    def has_webpush(self):
        return PushInformation.objects.filter(user=self).exists()

    def get_primary_language(self):
        logger.setLevel(logging.DEBUG)
        logger.debug("Trying to get the primary language of the user")
        if not hasattr(self, "person"):
            logger.debug("The user has no person linked, returning website language")
            return self.website_language

        if not hasattr(self.person, "mother_tongue"):
            logger.debug("The person has no mother tongue")
            return self.website_language

        language = self.person.mother_tongue
        if language:
            logger.debug("The person has a mother tongue: %s", language)
            return language

        default_first_language = settings.LANGUAGES[0][0]
        if default_first_language:
            logger.debug("Using default first language %s", default_first_language)
            return default_first_language

        return "en"

    @property
    def has_notifications(self):
        return self.notifications.count() > 0

    @cached_property
    def has_reservations(self):
        return self.reservations.count() > 0

    def set_first_and_family_name(
        self,
        first_name,
        family_name,
        *,
        overwrite_existing=False,
    ):
        if hasattr(self, "person"):
            self.person.set_first_and_family_name(
                first_name,
                family_name,
                overwrite_existing=overwrite_existing,
            )
