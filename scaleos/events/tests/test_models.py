import datetime

import pytest
from dateutil.relativedelta import relativedelta
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _

from scaleos.events import models as event_models
from scaleos.events.tests import model_factories as event_factories
from scaleos.organizations.tests import model_factories as organization_factories
from scaleos.payments.tests import model_factories as payment_factories
from scaleos.reservations.models import EventReservationSettings
from scaleos.reservations.tests import model_factories as reservation_factories
from scaleos.shared.mixins import ITS_NOW


# Add the new test class for CustomerConcept
@pytest.mark.django_db
class TestCustomerConcept:
    def test_clean_valid_customer_organizer_relationship(self):
        """
        Test that clean() passes when the customer belongs to the organizer.
        """
        organizer = organization_factories.OrganizationFactory.create()
        customer = organization_factories.OrganizationCustomerFactory.create(
            organization=organizer,
        )
        # Instantiate the CustomerConcept without saving,
        # as clean() is often called before save
        customer_concept = event_models.CustomerConcept(
            organizer=organizer,
            customer=customer,
            name="Valid Concept",
        )

        # clean() should not raise a ValidationError
        try:
            customer_concept.clean()
        except ValidationError as e:
            pytest.fail(f"clean() raised ValidationError unexpectedly: {e}")

    def test_clean_invalid_customer_organizer_relationship_raises_error(self):
        """
        Test that clean() raises a ValidationError when the customer
          does not belong to the organizer.
        """
        organizer1 = organization_factories.OrganizationFactory.create()
        organizer2 = organization_factories.OrganizationFactory.create()
        customer_of_org2 = organization_factories.OrganizationCustomerFactory.create(
            organization=organizer2,
        )

        # Instantiate the CustomerConcept with organizer1 but customer from organizer2
        customer_concept = event_models.CustomerConcept(
            organizer=organizer1,
            customer=customer_of_org2,
            name="Invalid Concept",
        )

        # Expect a ValidationError
        with pytest.raises(ValidationError) as excinfo:
            customer_concept.clean()

        # Check that the error is for the 'customer' field and has the correct message
        assert "customer" in excinfo.value.message_dict
        assert excinfo.value.message_dict["customer"] == [
            _("This is not one of your customers"),
        ]

    def test_save_sets_segment_b2b(self):
        """Test that saving sets segment to B2B if customer is B2B."""
        b2b_organization = organization_factories.OrganizationFactory.create()

        organizer = organization_factories.OrganizationFactory.create()
        customer = organization_factories.B2BCustomerFactory.create(
            organization=organizer,
            b2b_id=b2b_organization.pk,
        )
        customer_concept = event_models.CustomerConcept(
            organizer=organizer,
            customer=customer,
            name="B2B Concept",
            # segment defaults to BOTH initially
        )
        customer_concept.save()
        assert customer_concept.segment == event_models.Concept.SegmentType.B2B

    def test_save_sets_segment_b2c(self):
        """Test that saving sets segment to B2C if customer is B2C."""

        organizer = organization_factories.OrganizationFactory.create()
        customer = organization_factories.OrganizationCustomerFactory.create(
            organization=organizer,
        )
        customer_concept = event_models.CustomerConcept(
            organizer=organizer,
            customer=customer,
            name="B2C Concept",
            # segment defaults to BOTH initially
        )
        customer_concept.save()
        assert customer_concept.segment == event_models.Concept.SegmentType.B2C

    def test_str_method(self):
        """Test the __str__ representation."""
        organizer = organization_factories.OrganizationFactory.create()
        customer = organization_factories.OrganizationCustomerFactory.create(
            organization=organizer,
        )

        # Case 1: With name and customer
        concept1 = event_models.CustomerConcept(
            organizer=organizer,
            customer=customer,
            name="Special Deal",
        )
        assert str(concept1) == f"Special Deal - {customer}"

        # Case 2: With customer but no name
        concept2 = event_models.CustomerConcept(
            organizer=organizer,
            customer=customer,
            name="",  # Explicitly empty name
        )
        assert str(concept2) == f"{customer}"

        concept3 = event_models.CustomerConcept(
            organizer=organizer,
            customer=customer,
            # Name is None by default if not provided
        )
        assert str(concept3) == f"{customer}"

        # Case 3: No customer (should fall back to super().__str__ or default)
        # Note: This might not be a typical valid state due to clean()
        concept4 = event_models.CustomerConcept(
            organizer=organizer,
            customer=None,
            name="Generic Concept",
        )
        # Assuming super().__str__() returns something like the
        # class name and pk if saved
        # or a default representation if not saved. Let's test the name part.
        assert "Generic Concept" in str(concept4)


@pytest.mark.django_db
class TestEvent:
    def test_event_is_full(self):
        event = event_factories.EventFactory.create(maximum_number_of_guests=None)
        assert event.is_full is False

        event = event_factories.EventFactory.create(maximum_number_of_guests=10)
        assert event.is_full is False
        event.reserved_spots = 10
        event.save()
        assert event.is_full is True

    def test_event_has_free_spots(self):
        event = event_factories.EventFactory.create(maximum_number_of_guests=10)
        assert event.free_spots == 10
        event.reserved_spots = 5
        event.save()
        assert event.free_spots == 5

    def test_get_reserved_spots(self):
        event = event_factories.EventFactory.create(maximum_number_of_guests=10)
        assert event.get_reserved_spots() == 0
        event_reservation = reservation_factories.EventReservationFactory.create(
            event_id=event.pk,
        )
        event_reservation_line = reservation_factories.ReservationLineFactory.create(
            reservation_id=event_reservation.pk,
            amount=5,
        )
        event_reservation.lines.set([event_reservation_line])
        assert event_reservation.organization_confirm()
        assert event_reservation.requester_confirm()
        assert event_reservation.is_confirmed
        assert event_reservation.total_amount == 5
        assert event.get_reserved_spots() == 5

    def test_applicable_reservation_settings(self, faker):
        concept = event_factories.ConceptFactory.create()
        assert concept.reservation_settings is None
        event = event_factories.EventFactory.create(concept_id=concept.pk)
        assert event.applicable_reservation_settings is None

        settings_from_concept = (
            reservation_factories.EventReservationSettingsFactory.create()
        )
        concept.reservation_settings_id = settings_from_concept.pk
        concept.save()

        event.refresh_from_db()
        assert concept.reservation_settings is not None
        assert event.applicable_reservation_settings == settings_from_concept

        settings_from_event = (
            reservation_factories.EventReservationSettingsFactory.create()
        )
        event.reservation_settings_id = settings_from_event.pk
        event.save()

        assert event.applicable_reservation_settings == settings_from_event

    def test_applicable_event_reservation_payment_settings(self):
        concept = event_factories.ConceptFactory.create()
        assert concept.event_reservation_payment_settings is None
        event = event_factories.EventFactory.create(concept_id=concept.pk)
        assert event.event_reservation_payment_settings is None

        payment_settings_from_concept = (
            payment_factories.EventReservationPaymentSettingsFactory.create()
        )
        concept.event_reservation_payment_settings_id = payment_settings_from_concept.pk
        concept.save()

        event.refresh_from_db()
        assert concept.event_reservation_payment_settings is not None
        assert (
            event.applicable_event_reservation_payment_settings
            == payment_settings_from_concept
        )

        payment_settings_from_event = (
            payment_factories.EventReservationPaymentSettingsFactory.create()
        )
        event.event_reservation_payment_settings_id = payment_settings_from_event.pk
        event.save()

        assert (
            event.applicable_event_reservation_payment_settings
            == payment_settings_from_event
        )

    def test_show_progress_bar(self):
        event = event_factories.EventFactory.create(maximum_number_of_guests=100)
        assert event.show_progress_bar is False

        settings = reservation_factories.EventReservationSettingsFactory(
            always_show_progress_bar=False,
        )
        event.reservation_settings_id = settings.pk
        event.save()
        assert event.show_progress_bar is False

        settings = reservation_factories.EventReservationSettingsFactory(
            always_show_progress_bar=True,
        )
        event.reservation_settings_id = settings.pk
        event.save()
        assert event.show_progress_bar is True

        settings = reservation_factories.EventReservationSettingsFactory(
            show_progress_bar_when_x_percentage_reached=None,
        )
        event.reservation_settings_id = settings.pk
        assert event.show_progress_bar is False

        settings = reservation_factories.EventReservationSettingsFactory(
            show_progress_bar_when_x_percentage_reached=50,
        )
        event.reservation_settings_id = settings.pk
        event_reservation = reservation_factories.EventReservationFactory()
        reservation_factories.ReservationLineFactory(
            amount=50,
            reservation_id=event_reservation.pk,
        )
        event_reservation.save()
        event_reservation.organization_confirm()
        event_reservation.requester_confirm()
        event.refresh_from_db()

        assert event.show_progress_bar is True


@pytest.mark.django_db
class TestSingleEvent:
    def test_reservations_are_closed(self):
        birthday_event = event_factories.BirthdayEventFactory.create(
            allow_reservations=False,
        )
        assert birthday_event.reservations_are_closed is True

        birthday_event = event_factories.BirthdayEventFactory.create(
            allow_reservations=True,
        )
        assert birthday_event.reservations_are_closed is False

        settings = reservation_factories.EventReservationSettingsFactory.create(
            close_reservation_interval=EventReservationSettings.CloseReservationInterval.AT_START,
        )
        birthday_event = event_factories.BirthdayEventFactory.create(
            reservation_settings_id=settings.pk,
            starting_at=ITS_NOW,
        )
        assert birthday_event.reservations_are_closed is True


@pytest.mark.django_db
class TestBirthdayEvent:
    def test_warnings(self):
        birthday_event = event_factories.BirthdayEventFactory.create(
            allow_reservations=False,
        )
        assert len(birthday_event.warnings) >= 1

        birthday_person = event_factories.EventAttendeeFactory()
        event_factories.AttendeeRoleFactory.create(
            role=event_models.AttendeeRole.RoleType.BIRTHDAY_PERSON,
            event_attendee_id=birthday_person.pk,
        )
        birthday_event.attendees.add(birthday_person)
        assert len(birthday_event.warnings) == 0


@pytest.mark.django_db
def test_event_has_free_capacity(faker):  # noqa: PLR0915
    activate("nl")
    event = event_factories.EventFactory.create()
    assert event.free_spots == "∞"

    event.maximum_number_of_guests = 100
    event.save()

    assert event.free_spots == 100
    assert event.free_percentage == 100
    assert event.reserved_percentage == 0
    assert event.reserved_spots == 0

    event_reservation1_reservation_lines = (
        reservation_factories.ReservationLineFactory.create_batch(
            2,
            amount=15,
        )
    )

    event_reservation1 = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    event_reservation1.lines.set(event_reservation1_reservation_lines)
    assert event.reservations.count() == 1
    assert event.free_spots == 100
    assert event.free_percentage == 100
    assert event.reserved_percentage == 0
    assert event.reserved_spots == 0
    event_reservation1.requester_confirm()
    assert event_reservation1.requester_confirmed
    event_reservation1.organization_confirm()
    assert event_reservation1.organization_confirmed
    assert event_reservation1.is_confirmed

    event.refresh_from_db()
    assert event.free_spots == 70
    assert event.free_percentage == 70
    assert event.reserved_percentage == 30
    assert event.reserved_spots == 30
    assert event.over_reserved_spots == 0

    event_reservation2_reservation_lines = (
        reservation_factories.ReservationLineFactory.create_batch(2, amount=5)
    )
    event_reservation2 = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    event_reservation2.lines.set(event_reservation2_reservation_lines)
    event_reservation2.requester_confirm()
    event_reservation2.organization_confirm()
    event.refresh_from_db()

    assert event.free_spots == 60
    assert event.free_percentage == 60
    assert event.reserved_percentage == 40
    assert event.reserved_spots == 40
    assert event.over_reserved_spots == 0

    event_reservation3_reservation_lines = (
        reservation_factories.ReservationLineFactory.create_batch(6, amount=10)
    )
    event_reservation3 = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    event_reservation3.lines.set(event_reservation3_reservation_lines)
    event_reservation3.requester_confirm()
    event_reservation3.organization_confirm()
    event.refresh_from_db()
    assert event.free_spots == 0
    assert event.free_percentage == 0
    assert event.reserved_percentage == 100
    assert event.reserved_spots == 100
    assert event.over_reserved_spots == 0

    event_reservation4_reservation_lines = (
        reservation_factories.ReservationLineFactory.create_batch(5, amount=2)
    )
    event_reservation4 = reservation_factories.EventReservationFactory.create(
        event_id=event.pk,
    )
    event_reservation4.lines.set(event_reservation4_reservation_lines)
    event_reservation4.requester_confirm()
    event_reservation4.organization_confirm()
    event.refresh_from_db()
    assert event.free_spots == 0
    assert event.free_percentage == 0
    assert event.reserved_percentage == 100
    assert event.reserved_spots == 110
    assert event.over_reserved_spots == 10


@pytest.mark.django_db
def test_if_single_event_has_a_name(faker):
    expected_name = "single event"
    single_event = event_factories.SingleEventFactory.create(name=expected_name)
    assert expected_name == str(single_event)

    mkdate = datetime.datetime(year=2025, month=2, day=13, hour=11, minute=00)
    concept = event_factories.ConceptFactory.create(name="Brunch")
    single_event.concept_id = concept.pk
    single_event.starting_at = mkdate
    single_event.save()
    assert str(single_event) == "Brunch 2025-02-13"


@pytest.mark.django_db
def test_status_of_single_event(faker):
    single_event = event_factories.SingleEventFactory.create(
        starting_at=None,
        ending_on=None,
    )
    assert single_event.status == event_models.SingleEvent.STATUS.UNKNOWN, (
        "because no dates are set."
    )

    the_now = timezone.make_aware(
        datetime.datetime(
            year=2025,
            month=3,
            day=5,
            hour=11,
            minute=00,
            second=00,
        ),
        timezone.get_default_timezone(),
    )
    status = single_event.get_status(its_now=the_now)
    assert status == event_models.SingleEvent.STATUS.UNKNOWN

    yesterday = timezone.make_aware(
        datetime.datetime(
            year=2025,
            month=3,
            day=4,
            hour=11,
            minute=00,
            second=00,
        ),
        timezone.get_default_timezone(),
    )
    single_event.starting_at = yesterday
    single_event.ending_on = yesterday
    status = single_event.get_status(its_now=the_now)
    assert status == event_models.SingleEvent.STATUS.ENDED

    tomorrow = timezone.make_aware(
        datetime.datetime(
            year=2025,
            month=3,
            day=6,
            hour=11,
            minute=00,
            second=00,
        ),
        timezone.get_default_timezone(),
    )
    single_event.starting_at = tomorrow
    single_event.ending_on = tomorrow
    status = single_event.get_status(its_now=the_now)
    assert status == event_models.SingleEvent.STATUS.UPCOMING

    tomorrow = timezone.make_aware(
        datetime.datetime(
            year=2025,
            month=3,
            day=6,
            hour=11,
            minute=00,
            second=00,
        ),
        timezone.get_default_timezone(),
    )
    single_event.starting_at = tomorrow
    single_event.ending_on = None
    status = single_event.get_status(its_now=the_now)
    assert status == event_models.SingleEvent.STATUS.UPCOMING

    single_event.starting_at = yesterday
    single_event.ending_on = tomorrow
    status = single_event.get_status(its_now=the_now)
    assert status == event_models.SingleEvent.STATUS.ONGOING


@pytest.mark.django_db
def test_event_has_a_current_price_matrix(faker):
    from scaleos.payments.tests import model_factories as payment_factories

    today = timezone.make_aware(
        datetime.datetime(
            year=2025,
            month=3,
            day=6,
            hour=11,
            minute=00,
            second=00,
        ),
        timezone.get_default_timezone(),
    )
    two_years_ago = today - relativedelta(years=2)
    last_year = today - relativedelta(years=1)
    next_year = today + relativedelta(years=1)
    in_two_years = today + relativedelta(years=2)
    concept = event_factories.ConceptFactory()
    price_matrixes = payment_factories.PriceMatrixFactory.create_batch(6)
    event = event_factories.EventFactory(concept_id=concept.pk)

    assert hasattr(event, "current_price_matrix")
    assert event.current_price_matrix is None

    always_valid_price_matrix = event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        price_matrix_id=price_matrixes[0].pk,
    )
    assert hasattr(event, "current_price_matrix")
    assert event.current_price_matrix.id == always_valid_price_matrix.price_matrix.pk

    event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        price_matrix_id=price_matrixes[1].pk,
    )

    assert event.current_price_matrix is None, (
        "because we do not know which one to choose"
    )

    as_from_last_year_price_matrix = event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        valid_from=two_years_ago,
        price_matrix_id=price_matrixes[2].pk,
    )
    assert hasattr(event, "current_price_matrix")
    assert (
        event.current_price_matrix.id == as_from_last_year_price_matrix.price_matrix.pk
    )

    event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        valid_from=two_years_ago,
        valid_till=last_year,
        price_matrix_id=price_matrixes[3].pk,
    )
    current_concept_price_matrix = event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        valid_from=last_year,
        valid_till=next_year,
        price_matrix_id=price_matrixes[4].pk,
    )
    event_factories.ConceptPriceMatrixFactory.create(
        concept_id=concept.pk,
        valid_from=next_year,
        valid_till=in_two_years,
        price_matrix_id=price_matrixes[5].pk,
    )
    assert event.current_price_matrix.id == current_concept_price_matrix.price_matrix.pk


@pytest.mark.django_db
def test_event_reservations_closed_on(faker):
    event_reservation_settings = (
        reservation_factories.EventReservationSettingsFactory.create()
    )
    single_event = event_factories.SingleEventFactory.create(
        reservation_settings_id=event_reservation_settings.pk,
        starting_at=ITS_NOW,
    )
    assert single_event.reservations_closed_on


@pytest.mark.django_db
def test_event_duplicator(faker):
    starting_at = datetime.datetime(year=2025, month=3, day=30, hour=12, minute=00)
    brunch_event = event_factories.BrunchEventFactory.create(
        starting_at=starting_at,
        ending_on=starting_at + datetime.timedelta(hours=4),
    )
    assert brunch_event.pk
    a_from_date = datetime.date(year=2025, month=3, day=30)
    a_to_date = datetime.date(year=2025, month=4, day=11)
    event_duplicator = event_factories.EventDuplicatorFactory.create(
        event_id=brunch_event.pk,
        from_date=a_from_date,
        to_date=a_to_date,
        amount=1,
        every_interval=event_models.EventDuplicator.DuplicateInterval.EVERY_WEEK,
    )

    event_duplicator.duplicate()
    assert event_duplicator
    assert (
        event_models.SingleEvent.objects.filter(
            duplicator_id=event_duplicator.pk,
        ).count()
        == 2
    )
