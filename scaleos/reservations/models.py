import logging

from allauth.account.models import EmailAddress
from allauth.account.models import EmailConfirmation
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from moneyed import EUR
from moneyed import Money
from polymorphic.models import PolymorphicModel

from scaleos.notifications import models as notification_models
from scaleos.organizations import models as organization_models
from scaleos.organizations.models import Organization
from scaleos.payments.models import Price
from scaleos.reservations.tasks import send_reservation_update_notification
from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.functions import valid_email_address
from scaleos.shared.mixins import ITS_NOW
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.models import CardModel
from scaleos.users.models import User

# Create your models here.
logger = logging.getLogger(__name__)


class Reservation(
    PolymorphicModel,
    AdminLinkMixin,
    LogInfoFields,
    PublicKeyField,
    CardModel,
):
    class STATUS(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", _("in progress")
        TO_BE_CONFIRMED_BY_REQUESTER = (
            "TO_BE_CONFIRMED_BY_REQUESTER",
            _(
                "to be confirmed by requester",
            ),
        )
        TO_BE_CONFIRMED_BY_ORGANIZATION = (
            "TO_BE_CONFIRMED_BY_ORGANIZATION",
            _(
                "to be confirmed by organization",
            ),
        )
        ON_WAITINGLIST = "ON_WAITINGLIST", _("on waitinglist")
        WAITING_FOR_PAYMENT = "WAITING_FOR_PAYMENT", _("waiting for payment")
        PARTIALLY_PAID = "PARTIALLY_PAID", _("partially paid")
        PARTIALLY_USED = "PARTIALLY_USED", _("partially used")
        USED = "USED", _("used")
        EVENT_OVER = "EVENT_OVER", _("event is over")
        ENDED = "ENDED", _("ended")
        UNKNOWN = "UNKNOWN", _("unknown")

    organization = models.ForeignKey(
        "organizations.Organization",
        verbose_name=_(
            "organization",
        ),
        related_name="reservations",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    user = models.ForeignKey(
        get_user_model(),
        related_name="reservations",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    start = models.DateTimeField(
        verbose_name=_(
            "start",
        ),
        null=True,
        blank=True,
        help_text=_("the moment the reservation starts"),
    )
    end = models.DateTimeField(
        verbose_name=_(
            "end",
        ),
        null=True,
        blank=True,
        help_text=_("the moment the reservation ends"),
    )
    finished_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("the moment the reservation has been made"),
    )
    expired_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("the moment the reservation is no longer valid"),
    )
    confirmed_on = models.DateTimeField(
        verbose_name=_(
            "confirmed on",
        ),
        null=True,
        blank=True,
        help_text=_("the moment the reservation has been confirmed from both parties"),
    )
    on_waitinglist_since = models.DateTimeField(
        verbose_name=_(
            "on waitinglist since",
        ),
        null=True,
        blank=True,
        help_text=_("the moment the reservation has been added to the waitinglist"),
    )

    payment_request = models.OneToOneField(
        "payments.PaymentRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    customer_comment = models.TextField(default="", blank=True)
    customer_telephone = models.CharField(max_length=20, default="", blank=True)
    price = GenericRelation(
        Price,
        content_type_field="unique_origin_content_type",
        object_id_field="unique_origin_object_id",
    )

    class Meta:
        verbose_name = _("reservation")
        verbose_name_plural = _("reservations")

    def get_total_price(self) -> Price:
        """return the total price VAT included
        A reservation line can have another VAT percentage
        """
        logger.debug("Getting the total price for the reservation %s", self.pk)
        total_price = Price(
            vat_included=Money(0, EUR),
        )
        for idx, line in enumerate(self.lines.all()):
            logger.info("Current reservation line %s", idx)
            if line.total_price:
                total_price.plus(line.total_price)
                logger.info(
                    "The total price is now %s",
                    total_price.vat_included,
                )
        logger.debug("Total price is calculated.")

        # We dont want to set the VAT stuff, because we are talking about different prices with different VATs  # noqa: E501

        logger.info("The total price is: %s", str(total_price))
        return total_price

    @property
    def total_amount(self):
        the_result = self.lines.all().aggregate(total=Sum("amount"))["total"]
        if the_result:
            return the_result

        return 0

    @property
    def verified_email_address(self):
        if self.user:
            try:
                return EmailAddress.objects.get(
                    email=self.user.email,
                    verified=True,
                ).email
            except EmailAddress.DoesNotExist:
                return None

        return None  # pragma: no cover

    @property
    def is_in_waiting_list(self):
        return self.on_waitinglist_since is not None

    @property
    def status(self):
        if self.on_waitinglist_since:
            return self.STATUS.ON_WAITINGLIST

        if self.finished_on is None:
            return self.STATUS.IN_PROGRESS

        if self.payment_request:
            if self.payment_request.payments.count() == 0:
                return self.STATUS.WAITING_FOR_PAYMENT
            if not self.payment_request.fully_paid:
                return self.STATUS.PARTIALLY_PAID

        return self.STATUS.UNKNOWN  # pragma: no cover

    def add_user(self, request, confirmation_email_address):
        user, user_created = User.objects.get_or_create(
            email=confirmation_email_address,
        )

        if user_created:
            user.username = confirmation_email_address.split("@")[0]
            email_address, email_created = EmailAddress.objects.get_or_create(
                user=user,
                email=confirmation_email_address,
                primary=True,
            )
            if email_created:
                email_confirmation = EmailConfirmation.create(email_address)
                email_confirmation_link = ""
                if request:
                    email_confirmation_link = request.build_absolute_uri(
                        reverse("account_confirm_email", args=[email_confirmation.key]),
                    )
                email_confirmation.sent = ITS_NOW
                email_confirmation.save()

                WaitingUserEmailConfirmation.objects.create(
                    reservation_id=self.pk,
                    send_notification=True,
                    email_confirmation_link=email_confirmation_link,
                )
                logger.info("New user created via a reservation.")

        if self.organization:
            customer = self.organization.add_b2c(user)
            logger.debug("We have customer %s", customer.pk)

        self.user_id = user.pk
        if request:
            language = translation.get_language()
            if language:
                user.website_language = language
                user.save(update_fields=["website_language"])
        self.save(update_fields=["user_id"])

    def update_confirmation_moment(self):
        confrimation_state = self.get_confirmation_state()
        if confrimation_state:
            logger.debug("Updating the reservation confirmation moment")
            self.confirmed_on = ITS_NOW
            if isinstance(self, EventReservation):
                self.event.add_reserved_spots(self.total_amount)
        else:
            logger.debug("Removing the confirmation moment")
            self.confirmed_on = None
        self.save(update_fields=["confirmed_on"])

    def organization_auto_confirm(self):
        logger.debug("Trying to auto confirm the reserveration for the organization")

        send_notification = True
        if not self.user.is_email_verified:
            logger.info(
                "do not sent a notification yet, \
                      because the email is not yet confirmed",
            )
            return False

        if isinstance(self, EventReservation):
            logger.debug("This is an event reservation")
            if not hasattr(self, "event") or self.event is None:
                msg = _("we need an event for an event reservation")
                raise ValueError(msg)

            unlimited_spots = self.event.has_unlimited_spots
            logger.debug("Event has unlimited spots? %s", unlimited_spots)

            free_spots = self.event.free_spots
            logger.debug("Free spots: %s", free_spots)

            logger.debug("Total to reserve: %s", self.total_amount)

            event = self.event
            if event.has_capacity_for(self):
                self.organization_confirm(send_notification=send_notification)
                return True

            logger.warning("The event is full, so if cannot be confirmed automatically")
            self.on_waitinglist_since = ITS_NOW
            self.save(update_fields=["on_waitinglist_since"])
            logger.debug("Create an update")
            OrganizationTemporarilyRejected.objects.create(
                reservation_id=self.pk,
                send_notification=send_notification,
                reason=OrganizationTemporarilyRejected.RejectReason.EVENT_FULL,
            )
            return False

        logger.info("The reservation cannot be auto confirmed")
        return False

    @property
    def organization_confirmed(self):
        the_update = self.latest_organization_update
        if the_update:
            return the_update.is_confirmed
        return False

    def organization_confirm(self, *, send_notification=True):
        if self.organization is None:
            logger.warning(
                "This reservation has no organization, so we cannot confirm it",
            )
            return False

        logger.info("organization is confirming the reservation with id: %s", self.pk)
        if self.organization_confirmed:
            logger.info(
                "The reservation %s is already confirmed by the organization",
                self.pk,
            )
            return False

        OrganizationConfirm.objects.create(
            reservation_id=self.pk,
            send_notification=send_notification,
        )

        logger.info(
            "The reservation %s has now been confirmed by the requester",
            self.pk,
        )
        self.update_payment_request()
        self.update_confirmation_moment()
        return True

    @property
    def requester_confirmed(self):
        logger.debug("Checking if the requester confirmed the reservation")
        the_update = self.latest_requester_update
        if the_update:
            return the_update.is_confirmed
        logger.debug("The reservation is not yet confirmed")
        return False

    def requester_auto_confirm(self, request=None):
        if self.created_by is None:
            logger.debug("We do not know yet who created the reservation")
            if request:
                logger.debug("We have a request, so maybe we can get the user")
                if request.user.is_authenticated:
                    logger.debug("Yes it is an authenticated user")
                    self.created_by_id = request.user.pk
                    self.save(update_fields=["created_by_id"])
                    logger.debug("saved the user id in created_by")
                else:
                    logger.info(
                        "We do not know who created the reservation, \
                            so we cannot auto confirm it for the requester",
                    )
                    return False

        if self.user.pk == self.created_by_id:
            logger.debug(
                "The requester for the event is the same as creating user, \
                    so auto confirm",
            )
            self.requester_confirm(send_notification=False)
            return True

        return False

    def requester_confirm(self, *, send_notification=True):
        logger.debug("requester is confirming the reservation with id: %s", self.pk)

        if self.requester_confirmed:
            logger.info(
                "The reseravtion %s is already confirmed by the requester",
                self.pk,
            )
            return False

        if self.user is None:
            logger.warning("This reservation has no user, so we cannot confirm it")
            return False

        logger.debug("Creating the requester confirm object")
        RequesterConfirm.objects.create(
            reservation_id=self.pk,
            send_notification=send_notification,
        )

        logger.info(
            "The reservation %s has now been confirmed by the requester",
            self.pk,
        )
        self.update_confirmation_moment()
        return True

    @property
    def total_payment_requests(self):
        from scaleos.payments.models import PaymentRequest

        return PaymentRequest.objects.filter(
            origin_object_id=self.pk,
            origin_content_type__model="reservation",
        ).count()

    @property
    def applicable_payment_settings(self):
        if isinstance(self, EventReservation):
            if self.event.event_reservation_payment_settings:
                return self.event.event_reservation_payment_settings
            if self.event.concept.event_reservation_payment_settings:
                return self.event.concept.event_reservation_payment_settings
        return None

    @property
    def applicable_reservation_settings(self):
        if isinstance(self, EventReservation):
            if self.event.applicable_reservation_settings:
                return self.event.applicable_reservation_settings
        return None

    def update_payment_request(self):
        from scaleos.payments.models import PaymentRequest

        logger.info("Updating payment request for the reservation with id: %s", self.pk)

        the_total_price = self.get_total_price()
        logger.debug("Total price: %s", the_total_price)
        if (
            the_total_price is None
            or the_total_price.vat_included is None
            or the_total_price.vat_included.amount == 0
        ):
            logger.info("No total price with VAT included for the reservation")
            return

        payment_request, created = PaymentRequest.objects.get_or_create(
            id=self.payment_request_id,
        )
        if created:
            logger.info("New payment request created")

        if self.organization:
            payment_request.to_organization_id = self.organization.pk
            the_total_price.organization_id = self.organization.pk

        payment_request.origin = self

        if self.applicable_payment_settings:
            payment_request.payment_settings_id = self.applicable_payment_settings.pk
        payment_request.save()
        self.payment_request_id = payment_request.pk
        self.save()
        payment_request.set_price_to_pay(the_total_price)
        payment_request.apply_payment_settings()  # needs to be the last line, otherwise the payment conditions are not created  # noqa: E501

    @property
    def latest_organization_update(self):
        logger.debug("Getting the latest organization update")
        latest_status = (
            self.updates.instance_of(
                OrganizationConfirm,
                OrganizationRefuse,
                OrganizationCancel,
            )
            .order_by("-created_on")
            .first()
        )
        logger.debug("Latest organization update: %s", latest_status)
        return latest_status

    @property
    def organization_status(self):
        the_update = self.latest_organization_update
        if isinstance(the_update, OrganizationConfirm):
            return _("confirmed")
        if isinstance(the_update, OrganizationRefuse):
            return _("refused")
        if isinstance(the_update, OrganizationCancel):
            return _("canceled")
        return _("pending")

    @property
    def latest_requester_update(self):
        logger.debug("Getting the latest requester update")
        latest_upate = (
            self.updates.instance_of(RequesterConfirm, RequesterCancel)
            .order_by("-created_on")
            .first()
        )
        logger.debug("Latest requester update: %s", latest_upate)
        return latest_upate

    @property
    def requester_status(self):
        the_update = self.latest_requester_update
        if isinstance(the_update, RequesterConfirm):
            return _("confirmed")
        if isinstance(the_update, RequesterCancel):
            return _("canceled")
        return _("pending")

    def get_confirmation_state(self):
        logger.debug("getting the confirmation state for the reservation")
        org_status = self.latest_organization_update
        req_status = self.latest_requester_update

        if org_status and req_status:
            if org_status.is_confirmed and req_status.is_confirmed:
                logger.debug("The reservation is confirmed from both parties")
                return True
        logger.debug("The reservation is not confirmed")
        return False

    @property
    def is_confirmed(self):
        return self.confirmed_on is not None

    def can_be_checked_in_by(self, user):
        logger.debug("Checking if reservation can be checked in by user.")
        if self.user_id == user.id:
            logger.debug("yes, by the requester self")
            return True, User

        if not hasattr(user, "person") or user.person is None:
            logger.debug("no because the user has no person")
            return False, None

        organization_id = self.organization_id
        if organization_id is None:
            logger.debug("no because the reservation has no organization")
            return False, None

        person_id_who_want_to_checkin = user.person_id
        logger.info("person_id_who_want_to_checkin: %s", person_id_who_want_to_checkin)

        if organization_models.OrganizationEmployee.objects.filter(
            organization_id=organization_id,
            person_id=person_id_who_want_to_checkin,
        ).exists():
            logger.debug("yes, by an employee")
            return True, organization_models.OrganizationEmployee

        if organization_models.OrganizationOwner.objects.filter(
            organization_id=organization_id,
            person_id=person_id_who_want_to_checkin,
        ).exists():
            logger.debug("yes, by the owner")
            return True, organization_models.OrganizationOwner

        logger.debug("no because there is no check for it")
        return False, None


class EventReservation(Reservation):
    event = models.ForeignKey(
        "events.Event",
        related_name="reservations",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )

    def __str__(self):
        str_event = _("event")
        str_for = _("for")
        event_name = None
        person_name = None
        if hasattr(self, "event") and hasattr(self.event, "name"):
            event_name = self.event.name

        if self.user and hasattr(self.user, "person"):
            person_name = self.user.person

        if event_name and person_name:
            return f"{event_name} {str_for} {person_name}"

        return f"{str_event} {str_for} {self.user}"


class ReservationUpdate(PolymorphicModel, LogInfoFields, AdminLinkMixin):
    is_confirmed = False
    notification_button_text_translation = _("open reservation")
    notification_button_text = notification_button_text_translation.upper()
    reservation = models.ForeignKey(
        Reservation,
        related_name="updates",
        on_delete=models.CASCADE,
        null=True,
    )

    send_notification = models.BooleanField(
        verbose_name=_("send notification"),
        null=True,
    )
    """ notification = models.ForeignKey(
        "notifications.Notification",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    ) """

    class Meta:
        verbose_name = _("reservation update")
        verbose_name_plural = _("reservation updates")
        ordering = ["-created_on"]

    passed_action = _("updated")

    @property
    def notification_button_link(self):
        return self.reservation.page_url

    def __str__(self):
        str_on = _("on")
        return f"{self.passed_action} {self.reservation} {str_on}: {self.created_on}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # True if this is a new object
        super().save(*args, **kwargs)

        if is_new and self.send_notification:
            send_reservation_update_notification.apply_async((self.id,), countdown=5)

    def send_notification_logic(self, klass=None):
        logger.info(
            "[NOTIFY] %s notification created with id #%s",
            self.model_name,
            self.id,
        )

        if klass is None:
            logger.warning("We do not know to whom to send the notification")
            return False

        if self.reservation is None:
            logger.warning(
                "we are requested to send a reservation update, \
                    but the reservation is none",
            )
            return False

        if self.reservation.organization is None:
            logger.warning(
                "we can only send notifications if \
                    we know which organization it is sending",
            )
            return False

        if klass == User:
            logger.debug("Creating the user notification object")
            notification_models.UserNotification.objects.create(
                sending_organization=self.reservation.organization,
                to_user=self.reservation.user,
                about_content_object=self,
            )
            return True

        if klass == Organization:
            logger.debug("Creating the organization notification object")
            notification_models.OrganizationNotification.objects.create(
                sending_organization=self.reservation.organization,
                to=notification_models.OrganizationNotification.NotificationTo.ORGANIZATION_EMPLOYEES,
                about_content_object=self,
            )
            return True

        if klass == GuestInvite:
            logger.debug("Creating the guest notification object")
            notification_models.UserNotification.objects.create(
                sending_organization=self.reservation.organization,
                to_user=self.to_user,
                about_content_object=self,
            )
        return False


class OrganizationConfirm(ReservationUpdate):
    passed_action = _("organization confirmed")
    is_confirmed = True
    notification_title_translation = _("your reservation has been confirmed")
    notification_title = f"{notification_title_translation}. ✅".capitalize()
    notification_button_text_translation = _("open reservation")
    notification_button_text = notification_button_text_translation.upper()

    def send_notification_logic(self):
        return super().send_notification_logic(User)


class OrganizationCancel(ReservationUpdate):
    passed_action = _("organization canceled")
    is_confirmed = False
    notification_title_translation = _("your reservation has been canceled")
    notification_title = f"{notification_title_translation}. ✘".capitalize()

    def send_notification_logic(self):
        return super().send_notification_logic(User)


class OrganizationTemporarilyRejected(ReservationUpdate):
    passed_action = _("organization temporarily rejected")
    is_confirmed = False
    notification_title_translation = _("your reservation has been temporarily rejected")
    notification_title = f"{notification_title_translation}. ⏳".capitalize()

    class RejectReason(models.TextChoices):
        EVENT_FULL = "EVENT_FULL", _("event full")
        EVENT_FULL_BUT_ON_WAITINGLIST = (
            "EVENT_FULL_BUT_ON_WAITINGLIST",
            _("event full but on waitinglist"),
        )
        UNKNOWN = "UNKNOWN", _("unknown")

    reason = models.CharField(
        verbose_name=_(
            "reason",
        ),
        max_length=50,
        choices=RejectReason.choices,
        default=RejectReason.UNKNOWN,
    )

    def send_notification_logic(self):
        return super().send_notification_logic(User)


class OrganizationRefuse(ReservationUpdate):
    passed_action = _("organization refused")
    is_confirmed = False
    notification_title_translation = _("a reservation has been refused")
    notification_title = f"{notification_title_translation}. ✘".capitalize()

    class RefuseReason(models.TextChoices):
        EVENT_FULL = "EVENT_FULL", _("event full")
        PERSON_BLOCKED = "PERSON_BLOCKED", _("person blocked")
        CUSTOM_REASON = "CUSTOM_REASON", _("custom reason")
        UNKNOWN = "UNKNOWN", _("unknown")

    reason = models.CharField(
        verbose_name=_(
            "reason",
        ),
        max_length=50,
        choices=RefuseReason.choices,
        default=RefuseReason.UNKNOWN,
    )

    custom_reason = models.TextField(
        verbose_name=_("custom reason"),
        default="",
        blank=True,
    )

    def send_notification_logic(self):
        return super().send_notification_logic(User)


class RequesterConfirm(ReservationUpdate):
    passed_action = _("requester confirmed")
    is_confirmed = True
    notification_title_translation = _("the requester has confirmed his reservation")
    notification_title = f"{notification_title_translation}. ✅".capitalize()

    def send_notification_logic(self):
        logger.debug(
            "executing the logic of the requester confirmation notification logic",
        )
        return super().send_notification_logic(Organization)


class RequesterCancel(ReservationUpdate):
    passed_action = _("requester canceled")
    is_confirmed = False
    notification_title_translation = _("the requester has canceled his reservation")
    notification_title = f"{notification_title_translation}. ✘".capitalize()

    def send_notification_logic(self):
        return super().send_notification_logic(Organization)


class GuestInvite(ReservationUpdate):
    passed_action = _("guest invited")
    notification_title_translation = _("you are invited")
    notification_title = f"{notification_title_translation}. 👤".capitalize()
    nmt = _("you are invited for a reservation")
    nmt2 = _(
        "open the reservation to get to know more about it",
    )
    notification_message = f"{nmt.capitalize()}.\n{nmt2.capitalize()}."

    first_name = models.CharField(default="", blank=True)
    family_name = models.CharField(default="", blank=True)
    email_address = models.EmailField(default="", blank=True)

    to_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def send_notification_logic(self):
        valid_email, invalid_reason = valid_email_address(self.email_address)
        if not valid_email:
            logger.info(
                "the email is not valid (%s), so do not send the notification",
                invalid_reason,
            )
            return False

        to_user, created = User.objects.get_or_create(
            email=self.email_address,
        )
        if created:
            logger.info(
                "We just created a new user with email %s via a guest invite",
                self.email_address,
            )
            self.reservation.organization.add_b2c(to_user)

        self.to_user_id = to_user.pk
        self.save(update_fields=["to_user_id"])

        to_user.set_first_and_family_name(
            self.first_name,
            self.family_name,
            overwrite_existing=False,
        )
        return super().send_notification_logic(GuestInvite)


class WaitingUserEmailConfirmation(ReservationUpdate):
    passed_action = _("waiting user email confirmation")
    notification_title_translation = _("please confirm your email address")
    notification_title = f"{notification_title_translation}. 🔔".capitalize()
    notification_button_text_translation = _("confirm now")
    notification_button_text = notification_button_text_translation.upper()
    email_confirmation_link = models.URLField(default="", blank=True)

    def send_notification_logic(self):
        if (
            self.reservation
            and hasattr(self.reservation, "user")
            and self.reservation.user is None
        ):
            logger.warning(
                "Reservation has no user, so we cannot send the notification \
                      that we are waiting for email confirmation",
            )
            return

        notification_models.UserNotification.objects.create(
            sending_organization=self.reservation.organization,
            to_user=self.reservation.user,
            about_content_object=self,
            button_link=self.email_confirmation_link,
        )


class InvalidReservation(ReservationUpdate):
    passed_action = _("invalid reservation")
    notification_title_translation = _("an invalid reservation has been made")
    notification_title = f"{notification_title_translation}. ❗".capitalize()

    class InvalidReason(models.TextChoices):
        INVALID_EMAIL = "INVALID_EMAIL", _("invalid email")
        NO_ACTIVE_ORGANIZATION = "NO_ACTIVE_ORGANIZATION", _("no active organization")
        UNKNOWN = "UNKNOWN", _("unknown")

    reason = models.CharField(
        verbose_name=_(
            "reason",
        ),
        max_length=50,
        choices=InvalidReason.choices,
        default=InvalidReason.UNKNOWN,
    )

    additional_info = models.TextField(
        verbose_name=_("additional info"),
        default="",
        blank=True,
    )

    def send_notification_logic(self):
        return super().send_notification_logic(Organization)


class ReservationSettings(PolymorphicModel, AdminLinkMixin):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    telephone_number_required = models.BooleanField(
        verbose_name=_("telephone number required"),
        default=True,
    )

    class Meta:
        verbose_name = _("reservation settings")
        verbose_name_plural = _("reservation settings")


class EventReservationSettings(ReservationSettings):
    class CloseReservationInterval(models.TextChoices):
        SECONDS = "seconds", _("seconds")
        MINUTES = "minutes", _("minutes")
        HOURS = "hours", _("hour")
        DAYS = "days", _("days")
        WEEKS = "weeks", _("weeks")
        MONTHS = "months", _("months")
        YEARS = "years", _("years")
        AT_START = "at_start", _("at start")
        WHEN_ENDED = "on_end", _("when ended")

    minimum_persons_per_reservation = models.IntegerField(
        verbose_name=_("minimum persons per reservation"),
        null=True,
        blank=False,
        default=1,
    )
    maximum_persons_per_reservation = models.IntegerField(
        verbose_name=_("maximum persons per reservation"),
        null=True,
        blank=False,
        default=30,
    )
    maximum_reservations_in_waitlist = models.IntegerField(
        verbose_name=_("maximum reservations in waitlist"),
        null=True,
        blank=False,
        default=60,
    )

    close_reservation_time_amount = models.IntegerField(
        verbose_name=_("close reservation time amount"),
        null=True,
        blank=True,
        default=2,
    )
    close_reservation_interval = models.CharField(
        verbose_name=_("close reservation interval"),
        max_length=50,
        choices=CloseReservationInterval.choices,
        default=CloseReservationInterval.DAYS,
        blank=True,
    )
    always_show_progress_bar = models.BooleanField(
        verbose_name=_("always show progress bar"),
        default=False,
    )
    show_progress_bar_when_x_percentage_reached = models.IntegerField(
        verbose_name=_("show progress bar when x percentage reached"),
        null=True,
        blank=True,
        default=65,
    )

    class Meta:
        verbose_name = _("event reservation settings")
        verbose_name_plural = _("event reservation settings")


class ReservationLine(AdminLinkMixin, PublicKeyField):
    reservation = models.ForeignKey(
        Reservation,
        related_name="lines",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )
    amount = models.IntegerField(null=True, blank=False)
    price_matrix_item = models.ForeignKey(
        "payments.PriceMatrixItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )

    class Meta:
        ordering = ["pk"]

    @property
    def total_price(self) -> Price | None:  # noqa: PLR0911
        if self.amount == 0:
            logger.info("The amount of persons is 0, thus returning an empty price")
            return None

        if self.price_matrix_item is None:
            return None

        a_price = self.price_matrix_item.current_price
        if a_price is None:
            return None

        if a_price.vat_included.amount == 0:
            logger.info("The price is 0, thus returning an empty price")
            return None

        if self.amount == 1:
            return a_price

        try:
            result = a_price.multiply(self.amount)
            logger.info("The multiplied price is %s", result)

        except AttributeError as e:
            logger.warning(e)
        else:
            return result

        return Price(input_price=Money(0, EUR))

    @property
    def minimum_amount(self):
        if self.price_matrix_item is None:
            return 0

        if not hasattr(self.price_matrix_item, "minimum_persons"):
            return 0

        if self.price_matrix_item.minimum_persons:
            return self.price_matrix_item.minimum_persons

        return 0

    @property
    def maximum_amount(self):
        if hasattr(self.reservation, "event") and hasattr(
            self.reservation.event,
            "free_spots",
        ):
            free_spots = self.reservation.event.free_spots
            if free_spots == "∞":
                return None
            if self.price_matrix_item and self.price_matrix_item.maximum_persons:
                if self.price_matrix_item.maximum_persons > free_spots:
                    return free_spots

        if self.price_matrix_item and self.price_matrix_item.maximum_persons:
            return self.price_matrix_item.maximum_persons
        return 10
