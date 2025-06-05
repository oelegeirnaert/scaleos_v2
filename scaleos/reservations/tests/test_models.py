import datetime
import logging

import pytest
from moneyed import EUR
from moneyed import Decimal
from moneyed import Money

from scaleos.events.tests import model_factories as event_factories
from scaleos.hr.tests import model_factories as hr_factories
from scaleos.notifications.models import UserNotification
from scaleos.organizations import models as organization_models
from scaleos.organizations.tests import model_factories as organization_factories
from scaleos.payments.tests import model_factories as payment_factories
from scaleos.reservations import models as reservation_models
from scaleos.reservations.tests import model_factories as reservation_factories
from scaleos.users.models import User
from scaleos.users.tests import model_factories as user_factories

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db


class TestReservation:
    def test_if_a_reservation_is_confirmed(self):
        reservation = reservation_factories.ReservationFactory()
        assert reservation.organization_confirm() is True
        assert reservation.requester_confirm() is True
        reservation.refresh_from_db()
        assert reservation.is_confirmed is True

    def test_update_confirmation_moment(self):
        reservation = reservation_factories.ReservationFactory()
        reservation.update_confirmation_moment()
        assert reservation.is_confirmed is False, (
            "should be false, because the organizer and request still needs to confirm"
        )

        reservation_factories.OrganizationConfirmFactory(
            reservation_id=reservation.pk,
        )

        assert reservation.updates.count() == 1, (
            "one update, because the organizer confirmed"
        )
        assert reservation.latest_organization_update is not None, (
            "because it is just confirmed by the organizer"
        )
        assert reservation.is_confirmed is False, (
            "the organization confirmed, but we are still waiting for the requester to confirm"  # noqa: E501
        )

        reservation_factories.RequesterConfirmFactory(
            reservation_id=reservation.pk,
        )
        assert reservation.updates.count() == 2, (
            "two updates, because the requester and organizer confirmed"
        )
        assert reservation.latest_requester_update is not None, (
            "because it is just confirmed by the requester"
        )
        reservation.refresh_from_db()
        assert reservation.confirmed_on is not None, (
            "should be set, because it is just confirmed by the requester and organization"  # noqa: E501
        )
        assert reservation.is_confirmed is True, (
            "should be true, because the requester and organizer confirmed"
        )

        reservation_factories.OrganizationCancelFactory(
            reservation_id=reservation.pk,
        )
        assert reservation.updates.count() == 3, (
            "three updates, because the organization canceled"
        )
        reservation.refresh_from_db()
        assert reservation.is_confirmed is False, (
            "should be false, because the organization canceled"
        )

    def test_requester_updates_till(self):
        starting_event = datetime.datetime(2025, 6, 4, 15, 30, tzinfo=datetime.UTC)
        event_reservation_settings = reservation_factories.EventReservationSettingsFactory(  # noqa: E501
            allow_requester_updates_until_time_amount=1,
            allow_requester_updates_until_interval=reservation_models.ReservationSettings.AllowRequesterUpdatesUntillInterval.DAYS,
        )
        event = event_factories.SingleEventFactory(
            starting_at=starting_event,
            reservation_settings_id=event_reservation_settings.pk,
        )
        reservation = reservation_factories.EventReservationFactory(event_id=event.pk)
        assert reservation.allow_requester_updates_until is not None
        blocked_datetime = starting_event - datetime.timedelta(days=1)
        assert reservation.allow_requester_updates_until == blocked_datetime, (
            "because it is blocked by the settings"
        )
        assert reservation.requester_can_update_on(starting_event) is False, (
            "because it is on the starting datetime"
        )
        allowed_datetime = starting_event - datetime.timedelta(days=2)
        assert reservation.requester_can_update_on(allowed_datetime) is True, (
            "because the expiry datetime is still in the future"
        )


class TestEventReservation:
    def test_event_reservation_start_date_is_set_from_start_of_event(self):
        event = event_factories.BirthdayEventFactory()
        event_reservation = reservation_factories.EventReservationFactory(
            event_id=event.pk,
        )
        assert event_reservation.start == event.starting_at
        assert event_reservation.end == event.ending_on


class TestGuestInvite:
    def test_guest_invite_will_receive_a_notification(self):
        organization = organization_factories.OrganizationFactory()
        reservation = reservation_factories.ReservationFactory(
            organization_id=organization.pk,
        )
        guest_invite = reservation_factories.GuestInviteFactory(
            reservation_id=reservation.pk,
        )

        assert hasattr(guest_invite, "email_address")
        guest_invite.email_address = "joske@hotmail.com"
        guest_invite.send_notification_logic()

        assert UserNotification.objects.count() == 1
        assert organization_models.Customer.objects.count() == 1


@pytest.mark.django_db
def test_brunch_reservation_for_waerboom(faker):
    from scaleos.payments.tests.model_factories import AgePriceMatrixFactory
    from scaleos.payments.tests.model_factories import AgePriceMatrixItemFactory
    from scaleos.payments.tests.model_factories import PriceFactory

    brunch_concept = event_factories.ConceptFactory.create()
    age_price_matrix = AgePriceMatrixFactory.create()

    the_baby_price = Money(0.0, EUR)

    baby_price_matrix_item = AgePriceMatrixItemFactory.create(
        till_age=4,
        age_price_matrix_id=age_price_matrix.pk,
    )
    PriceFactory.create(
        vat_included=the_baby_price,
        unique_origin=baby_price_matrix_item,
    )

    the_children_price = Money(10, EUR)

    children_price_matrix_item = AgePriceMatrixItemFactory.create(
        from_age=5,
        till_age=12,
        age_price_matrix_id=age_price_matrix.pk,
    )
    PriceFactory.create(
        vat_included=the_children_price,
        unique_origin=children_price_matrix_item,
    )

    the_adolescent_price = Money(20, EUR)

    adolescent_price_matrix_item = AgePriceMatrixItemFactory.create(
        from_age=13,
        till_age=16,
        age_price_matrix_id=age_price_matrix.pk,
    )
    PriceFactory.create(
        vat_included=the_adolescent_price,
        unique_origin=adolescent_price_matrix_item,
    )

    the_adult_price = Money(30, EUR)

    adult_price_matrix_item = AgePriceMatrixItemFactory.create(
        from_age=17,
        age_price_matrix_id=age_price_matrix.pk,
    )
    PriceFactory.create(
        vat_included=the_adult_price,
        unique_origin=adult_price_matrix_item,
    )

    event_factories.ConceptPriceMatrixFactory.create(
        concept_id=brunch_concept.pk,
        price_matrix_id=age_price_matrix.pk,
    )
    assert brunch_concept.current_price_matrix, "check if the brunc has a price matrix"

    brunch_event = event_factories.BrunchEventFactory.create(
        concept_id=brunch_concept.pk,
    )
    brunch_reservation = reservation_factories.BrunchReservationFactory.create(
        event_id=brunch_event.pk,
    )

    person = hr_factories.PersonFactory.create()

    brunch_reservation.person_id = person.pk
    brunch_reservation.save()

    assert Money(0, EUR) == brunch_reservation.get_total_price().vat_included, (
        "because we haven't any reservation lines yet"
    )
    assert brunch_event.current_price_matrix, (
        "We must have a price matrix in order to be able to do the calculations"
    )

    brunch_reservation.used_price_matrix = brunch_event.current_price_matrix
    brunch_reservation.save()

    number_of_babies = 3
    baby_reservation_line = reservation_factories.ReservationLineFactory.create(
        reservation_id=brunch_reservation.pk,
        amount=number_of_babies,
        price_matrix_item_id=baby_price_matrix_item.pk,
    )
    assert baby_reservation_line.total_price is None

    number_of_children = 5
    children_reservation_line = reservation_factories.ReservationLineFactory.create(
        reservation_id=brunch_reservation.pk,
        amount=number_of_children,
        price_matrix_item_id=children_price_matrix_item.pk,
    )
    assert (
        the_children_price * number_of_children
        == children_reservation_line.total_price.vat_included
    )

    number_of_adolescents = 2
    adolescent_reservation_line = reservation_factories.ReservationLineFactory.create(
        reservation_id=brunch_reservation.pk,
        amount=number_of_adolescents,
        price_matrix_item_id=adolescent_price_matrix_item.pk,
    )
    assert (
        number_of_adolescents * the_adolescent_price
        == adolescent_reservation_line.total_price.vat_included
    )

    number_of_adults = 4
    adults_reservation_line = reservation_factories.ReservationLineFactory.create(
        reservation_id=brunch_reservation.pk,
        amount=number_of_adults,
        price_matrix_item_id=adult_price_matrix_item.pk,
    )
    assert (
        number_of_adults * the_adult_price
        == adults_reservation_line.total_price.vat_included
    )

    assert (
        children_reservation_line.total_price.vat_included
        + adolescent_reservation_line.total_price.vat_included
        + adults_reservation_line.total_price.vat_included
        == brunch_reservation.get_total_price().vat_included
    )


@pytest.mark.django_db
def test_brunch_reservationline_for_waerboom_has_min_max_persons(faker):
    from scaleos.payments.tests.model_factories import AgePriceMatrixItemFactory

    minimum = 8
    maximum = 13
    age_price_matrix_item = AgePriceMatrixItemFactory.create(
        minimum_persons=minimum,
        maximum_persons=maximum,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        price_matrix_item_id=age_price_matrix_item.pk,
    )
    assert hasattr(reservation_line, "minimum_amount")
    assert hasattr(reservation_line, "maximum_amount")
    assert minimum == reservation_line.minimum_amount
    assert maximum == reservation_line.maximum_amount


@pytest.mark.django_db
def test_brunch_reservationline_for_waerboom_cannot_exceed_total_availble_places(faker):
    from scaleos.payments.tests.model_factories import AgePriceMatrixItemFactory

    max_spots = 100
    line_max = 5
    brunch = event_factories.BrunchEventFactory.create(
        maximum_number_of_guests=max_spots,
    )
    assert max_spots == brunch.free_spots
    age_price_matrix_item = AgePriceMatrixItemFactory.create(
        maximum_persons=line_max,
    )
    event_reservation = reservation_factories.EventReservationFactory(
        event_id=brunch.pk,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        price_matrix_item_id=age_price_matrix_item.pk,
        reservation_id=event_reservation.pk,
    )
    assert line_max == reservation_line.maximum_amount

    max_spots = 3
    small_brunch = event_factories.BrunchEventFactory.create(
        maximum_number_of_guests=max_spots,
    )
    very_large_event_reservation = reservation_factories.EventReservationFactory(
        event_id=small_brunch.pk,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        price_matrix_item_id=age_price_matrix_item.pk,
        reservation_id=very_large_event_reservation.pk,
    )
    assert max_spots == small_brunch.free_spots
    assert max_spots == reservation_line.maximum_amount, (
        f"because we only have {small_brunch.free_spots} free spots in the event"
    )

    brunch_unlimited_seats = event_factories.BrunchEventFactory.create(
        maximum_number_of_guests=None,
    )
    unlimited_event_reservation = reservation_factories.EventReservationFactory(
        event_id=brunch_unlimited_seats.pk,
    )
    reservation_line = reservation_factories.ReservationLineFactory.create(
        price_matrix_item_id=age_price_matrix_item.pk,
        reservation_id=unlimited_event_reservation.pk,
    )
    assert brunch_unlimited_seats.free_spots == "∞"
    assert reservation_line.maximum_amount is None, (
        "because we only have unlimited free spots in the event"
    )


@pytest.mark.django_db
def test_reservation_has_total_amount(faker):
    reservation = reservation_factories.ReservationFactory.create()
    assert reservation.total_amount == 0
    reservation_factories.ReservationLineFactory.create_batch(
        3,
        reservation_id=reservation.pk,
        amount=3,
    )
    assert reservation.total_amount == 9


@pytest.mark.django_db
def test_reservation_is_human_verified(faker):
    the_email = "my_email@hotmail.com"

    user = user_factories.UserFactory(email=the_email)
    user_factories.EmailAddressFactory(user=user, email=user.email)

    reservation = reservation_factories.ReservationFactory(user=user)
    assert reservation.verified_email_address == the_email


@pytest.mark.django_db
def test_reservation_is_not_human_verified(faker):
    the_email = "my_email@hotmail.com"

    user = user_factories.UserFactory(email=the_email)

    reservation = reservation_factories.ReservationFactory(user=user)
    assert reservation.verified_email_address is None


@pytest.mark.django_db
def test_reservation_requester_confirm(faker):
    reservation = reservation_factories.ReservationFactory()
    reservation.requester_confirm()
    assert reservation.requester_confirmed
    assert not reservation.requester_confirm(), "because it is already confirmed"


@pytest.mark.django_db
def test_reservation_without_user_cannot_be_confirmed(faker):
    reservation = reservation_factories.ReservationFactory()
    reservation.user = None
    reservation.requester_confirm()
    assert reservation.requester_confirmed is False


@pytest.mark.django_db
def test_reservation_that_is_already_confirmed_by_requester_cannot_be_confirmed(faker):
    reservation = reservation_factories.ReservationFactory()
    reservation.requester_confirm()
    assert reservation.requester_confirmed is True
    assert reservation.requester_confirm() is False


@pytest.mark.django_db
def test_reservation_organization_confirm(faker):
    reservation = reservation_factories.ReservationFactory()
    reservation.organization_confirm()
    assert reservation.organization_confirmed
    assert not reservation.organization_confirm(), "because it is already confirmed"


@pytest.mark.django_db
def test_reservation_that_is_already_confirmed_by_organization_cannot_be_confirmed(
    faker,
):
    reservation = reservation_factories.ReservationFactory()
    assert reservation.organization_confirm() is True
    assert reservation.organization_confirmed is True
    assert reservation.organization_confirm() is False, (
        "because it is already confirmed"
    )


@pytest.mark.django_db
def test_reservation_payment_request(faker):
    hundred_euro = Money(100, EUR)

    age_price_matrix = payment_factories.AgePriceMatrixFactory()
    age_price_matrix_item = payment_factories.AgePriceMatrixItemFactory(
        age_price_matrix_id=age_price_matrix.pk,
    )
    payment_factories.PriceFactory.create(
        vat_included=hundred_euro,
        unique_origin=age_price_matrix_item,
    )

    brunch_concept = event_factories.ConceptFactory()
    event_factories.ConceptPriceMatrixFactory(
        price_matrix_id=age_price_matrix.pk,
        concept_id=brunch_concept.pk,
    )
    brunch_event = event_factories.BrunchEventFactory(concept_id=brunch_concept.pk)

    reservation = reservation_factories.EventReservationFactory(
        event_id=brunch_event.pk,
    )
    reservation_factories.ReservationLineFactory(
        reservation_id=reservation.pk,
        amount=1,
        price_matrix_item_id=age_price_matrix_item.pk,
    )
    assert reservation.lines.count() == 1

    assert reservation.get_total_price()
    assert reservation.get_total_price().vat_included
    assert reservation.get_total_price().vat_included.amount == Decimal(100.00)
    reservation.organization_confirm()
    reservation.requester_confirm()
    reservation.refresh_from_db()
    assert reservation.is_confirmed is True, "both parties confirmed the reservation"
    assert reservation.payment_request, (
        "when both parties confirmed the reservation, there should be a payment request"
    )


@pytest.mark.django_db
def test_update_payment_request_updates_existing_payment_request_and_price(
    faker,
):
    """
    Test that if there's an existing payment_request, it will update it
    and the price.
    """

    payment_request = payment_factories.PaymentRequestFactory()
    payment_factories.PriceFactory(
        vat_included=Money(50, EUR),
        unique_origin=payment_request,
    )
    reservation = reservation_factories.ReservationFactory(
        payment_request=payment_request,
    )
    reservation.update_payment_request()
    assert payment_request.to_pay.vat_included == Money(50, EUR)

    age_price_matrix = payment_factories.AgePriceMatrixFactory()
    age_price_matrix_item = payment_factories.AgePriceMatrixItemFactory(
        age_price_matrix_id=age_price_matrix.pk,
    )
    hundred_euro = Money(100, EUR)
    payment_factories.PriceFactory.create(
        vat_included=hundred_euro,
        unique_origin=age_price_matrix_item,
    )

    reservation_factories.ReservationLineFactory(
        reservation=reservation,
        amount=2,
        price_matrix_item_id=age_price_matrix_item.pk,
    )
    reservation.update_payment_request()
    assert payment_request.to_pay.vat_included == Money(200, EUR)


@pytest.mark.django_db
def test_total_price_vat_included_no_price(faker):
    """
    Test that total_price_vat_included returns None and logs a warning
    when there is no price.
    """
    age_price_matrix_item = payment_factories.AgePriceMatrixItemFactory()
    reservation_line = reservation_factories.ReservationLineFactory(
        amount=3,
        price_matrix_item=age_price_matrix_item,
    )
    assert reservation_line.total_price is None


@pytest.mark.django_db
def test_event_reservation_is_automatically_confired_by_organization_when_there_is_enough_free_space(  # noqa: E501
    faker,
):
    event = event_factories.BrunchEventFactory.create(maximum_number_of_guests=10)
    assert event.free_spots == 10
    event_reservation = reservation_factories.EventReservationFactory(event_id=event.pk)
    reservation_factories.ReservationLineFactory.create(
        reservation_id=event_reservation.pk,
        amount=1,
    )
    assert event.free_spots == 10
    assert event_reservation.requester_confirm()
    assert event_reservation.requester_confirmed
    assert event_reservation.organization_confirm()
    assert event_reservation.organization_confirmed
    event.refresh_from_db()
    assert event.free_spots == 9


@pytest.mark.django_db
def test_event_can_have_a_waitlist(faker, verified_user):
    event_reservation_settings = reservation_factories.EventReservationSettingsFactory()
    event = event_factories.BirthdayEventFactory(
        reservation_settings_id=event_reservation_settings.pk,
        maximum_number_of_guests=10,
    )
    event_reservation = reservation_factories.EventReservationFactory(event_id=event.pk)
    reservation_factories.ReservationLineFactory(
        reservation_id=event_reservation.pk,
        amount=9,
    )
    event_reservation.organization_confirm()
    event_reservation.requester_confirm()
    assert event_reservation.on_waitinglist_since is None

    event_reservation_big_group = reservation_factories.EventReservationFactory(
        event_id=event.pk,
        user_id=verified_user.pk,
    )
    reservation_factories.ReservationLineFactory(
        reservation_id=event_reservation_big_group.pk,
        amount=30,
    )

    assert event_reservation_big_group.requester_confirm() is True
    assert event_reservation_big_group.organization_auto_confirm() is False
    assert event_reservation_big_group.on_waitinglist_since is not None
    assert event_reservation_big_group.is_confirmed is False


@pytest.mark.django_db
def test_organization_cannot_autoconfirm_when_user_not_verified(faker):
    event = event_factories.BirthdayEventFactory()
    event_reservation = reservation_factories.EventReservationFactory(event_id=event.pk)
    assert event_reservation.organization_auto_confirm() is False


@pytest.mark.django_db
def test_reservation_can_be_checked_in_by_user(faker, verified_user):
    reservation = reservation_factories.ReservationFactory(user_id=verified_user.pk)
    result, result_type = reservation.can_be_checked_in_by(verified_user)
    assert result
    assert result_type == User


@pytest.mark.django_db
def test_reservation_can_be_checked_in_by_organization_employee(faker, verified_user):
    organization = organization_models.Organization.objects.create()
    organization_employee = organization_models.OrganizationEmployee.objects.create(
        person_id=verified_user.person.pk,
        organization_id=organization.pk,
    )
    reservation = reservation_factories.ReservationFactory(
        user_id=verified_user.pk,
        organization_id=organization.id,
    )
    result, result_type = reservation.can_be_checked_in_by(organization_employee)
    assert result
    assert result_type == organization_models.OrganizationEmployee


@pytest.mark.django_db
def test_reservation_can_be_checked_in_by_organization_owner(faker, verified_user):
    organization = organization_models.Organization.objects.create()
    organization_owner = organization_models.OrganizationOwner.objects.create(
        person_id=verified_user.person.pk,
        organization_id=organization.pk,
    )
    reservation = reservation_factories.ReservationFactory(
        user_id=verified_user.pk,
        organization_id=organization.id,
    )
    result, result_type = reservation.can_be_checked_in_by(organization_owner)
    assert result
    assert result_type == organization_models.OrganizationOwner
