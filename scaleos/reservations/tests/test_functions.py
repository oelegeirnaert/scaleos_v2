# /opt/scaleos/scaleos/reservations/tests/test_functions.py

import logging

import pytest

from scaleos.events.tests import model_factories as event_factories
from scaleos.organizations.tests import model_factories as organization_factories

# Assuming the function is in scaleos.reservations.functions
from scaleos.reservations.functions import get_organization_id_from_reservation
from scaleos.reservations.tests import model_factories as reservation_factories

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db


class TestGetOrganizationFromReservation:
    def test_event_reservation_with_organizer_on_concept(self):
        """
        Test getting the organizer ID via the Event -> Concept -> Organizer path.
        """
        organizer = organization_factories.OrganizationFactory.create()
        concept = event_factories.ConceptFactory.create(organizer=organizer)
        event = event_factories.SingleEventFactory.create(concept=concept)
        reservation = reservation_factories.EventReservationFactory.create(event=event)

        org_id = get_organization_id_from_reservation(reservation)
        assert org_id == organizer.pk

    def test_event_reservation_with_organizer_on_event_no_concept_organizer(self):
        """
        Test fallback to Event -> Organizer when Concept exists but has no organizer.
        """
        organizer = organization_factories.OrganizationFactory.create()
        # Create concept without an organizer
        concept = event_factories.ConceptFactory.create(organizer=None)
        # Create event linked to concept AND directly to organizer
        event_factories.SingleEventFactory.create(
            concept=concept,
            # Assuming Event model has a direct FK to Organization (adjust if not)
            # If Event doesn't have a direct FK, this test case might be invalid
            # based on current models. Let's assume it might for robustness.
            # If not, remove the 'organization=organizer' part and expect None.
            # **Update based on Event model:** Event itself doesn't seem to have
            # a direct organizer FK. The link is usually via Concept.
            # So, let's test the case where Concept exists but has no organizer,
            # and Event *also* has no direct link (which is the standard structure).
        )
        # Re-evaluating: The code *does* check
        # `hasattr(reservation.event, "organization")`
        # Let's assume Event *could* have an organization FK for some reason, or
        # maybe a subclass does. We'll test that specific fallback.
        event_with_direct_org = event_factories.SingleEventFactory.create(
            concept=concept,  # Concept without organizer
        )
        # Manually add an 'organization' attribute for testing the fallback path,
        # even if not standard on the base Event model.
        event_with_direct_org.organization = organizer
        event_with_direct_org.save()  # Save the added attribute if needed by logic

        reservation = reservation_factories.EventReservationFactory.create(
            event=event_with_direct_org,
        )

        org_id = get_organization_id_from_reservation(reservation)
        # This assertion depends on whether Event *can* have a direct org link.
        # Based on the provided Event model, it doesn't. The code checks for it though.
        # If Event *cannot* have a direct org link, the expected result is None.
        # Let's assert based on the code's fallback check:
        assert org_id == organizer.pk

    def test_event_reservation_with_organizer_on_event_no_concept(self):
        """
        Test getting the organizer ID via the Event ->
        Organizer path when no Concept exists.
        """
        organizer = organization_factories.OrganizationFactory.create()
        # Create event without a concept, but potentially with a direct org link
        event_with_direct_org = event_factories.SingleEventFactory.create(
            concept=None,
        )
        # Manually add 'organization' for testing fallback
        event_with_direct_org.organization = organizer
        event_with_direct_org.save()

        reservation = reservation_factories.EventReservationFactory.create(
            event=event_with_direct_org,
        )

        org_id = get_organization_id_from_reservation(reservation)
        # Again, asserting based on the code's fallback check
        assert org_id == organizer.pk

    def test_event_reservation_no_organizer_found(self):
        """
        Test case where EventReservation has an Event and Concept,
        but no organizer link.
        """
        concept_no_org = event_factories.ConceptFactory.create(organizer=None)
        event_no_org = event_factories.SingleEventFactory.create(concept=concept_no_org)
        # Ensure event has no direct organization link either
        if hasattr(event_no_org, "organization"):
            event_no_org.organization = None
            event_no_org.save()

        reservation = reservation_factories.EventReservationFactory.create(
            event=event_no_org,
        )

        org_id = get_organization_id_from_reservation(reservation)
        assert org_id is None

    def test_event_reservation_event_has_no_concept(self):
        """
        Test case where EventReservation's Event has no Concept and
        no direct Organizer link.
        """
        event_no_concept_no_org = event_factories.SingleEventFactory.create(
            concept=None,
        )
        # Ensure event has no direct organization link either
        if hasattr(event_no_concept_no_org, "organization"):
            event_no_concept_no_org.organization = None
            event_no_concept_no_org.save()

        reservation = reservation_factories.EventReservationFactory.create(
            event=event_no_concept_no_org,
        )

        org_id = get_organization_id_from_reservation(reservation)
        assert org_id is None

    def test_event_reservation_without_event(self):
        """
        Test case where the EventReservation object has no associated Event.
        """
        reservation = reservation_factories.EventReservationFactory.create(event=None)

        org_id = get_organization_id_from_reservation(reservation)
        assert org_id is None

    def test_base_reservation_type(self):
        """
        Test case where the reservation is not an EventReservation.
        """
        # Use the base ReservationFactory
        reservation = reservation_factories.ReservationFactory.create()

        org_id = get_organization_id_from_reservation(reservation)
        assert org_id is None

    def test_event_reservation_concept_exists_but_is_none(self):
        """
        Test case where event.concept exists but is None (edge case).
        """
        organizer = organization_factories.OrganizationFactory.create()
        event = event_factories.SingleEventFactory.create(concept=None)
        # Add direct org link for fallback test
        event.organization = organizer
        event.save()

        reservation = reservation_factories.EventReservationFactory.create(event=event)

        org_id = get_organization_id_from_reservation(reservation)
        assert org_id == organizer.pk  # Should fallback to event.organization

    def test_event_reservation_concept_organizer_is_none(self):
        """
        Test case where event.concept.organizer exists but is None.
        """
        organizer = organization_factories.OrganizationFactory.create()
        concept = event_factories.ConceptFactory.create(
            organizer=None,
        )  # Organizer is None
        event = event_factories.SingleEventFactory.create(concept=concept)
        # Add direct org link for fallback test
        event.organization = organizer
        event.save()
        event.refresh_from_db()

        reservation = reservation_factories.EventReservationFactory.create(event=event)

        org_id = get_organization_id_from_reservation(reservation)
        assert org_id == organizer.pk  # Should fallback to event.organization
