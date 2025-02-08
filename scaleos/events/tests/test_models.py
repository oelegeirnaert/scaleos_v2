from django.test import TestCase
from scaleos.events import models as event_models
from scaleos.events.tests import model_factories as event_factories
from scaleos.reservations.tests import model_factories as reservation_factories
import pytest
from uuid import uuid4
import logging
import datetime
from moneyed import Money, EUR, USD
from django.utils import timezone
from django.utils.translation import activate
from django.conf import settings

@pytest.mark.django_db
def test_brunchconcept_can_generate_events(faker): 
    brunch_concept = event_factories.BrunchConceptFactory.create()
    from_date = datetime.date(year=2025, month=2, day=1)
    to_date = datetime.date(year=2025, month=3, day=1)
    weekday = 7
    brunch_concept.generate(from_date, to_date, weekday)
    assert 4 == brunch_concept.events.count(), "4 sundays in feb 2025"

@pytest.mark.django_db
def test_brunch_has_free_capacity(faker): 
    activate('nl')
    brunch_event = event_factories.BrunchEventFactory.create()

    assert "ongelimiteerd" == brunch_event.free_spots

    brunch_event.maximum_number_of_guests = 100

    assert 100 == brunch_event.free_spots
    assert 100 == brunch_event.free_percentage
    assert 0 == brunch_event.reserved_percentage
    assert 0 == brunch_event.reserved_spots

    brunch_reservations = reservation_factories.BrunchReservationFactory.create_batch(4, brunch_event_id=brunch_event.pk)
    brunch_reservations[0].amount = 30
    brunch_reservations[0].save()
    assert 70 == brunch_event.free_spots
    assert 70 == brunch_event.free_percentage
    assert 30 == brunch_event.reserved_percentage
    assert 30 == brunch_event.reserved_spots

    brunch_reservations[1].amount = 10
    brunch_reservations[1].save()
    assert 60 == brunch_event.free_spots
    assert 60 == brunch_event.free_percentage
    assert 40 == brunch_event.reserved_percentage
    assert 40 == brunch_event.reserved_spots
    assert 0 == brunch_event.over_reserved_spots

    brunch_reservations[2].amount = 60
    brunch_reservations[2].save()
    assert 0 == brunch_event.free_spots
    assert 0 == brunch_event.free_percentage
    assert 100 == brunch_event.reserved_percentage
    assert 100 == brunch_event.reserved_spots
    assert 0 == brunch_event.over_reserved_spots

    brunch_reservations[3].amount = 10
    brunch_reservations[3].save()
    assert 0 == brunch_event.free_spots
    assert 0 == brunch_event.free_percentage
    assert 100 == brunch_event.reserved_percentage
    assert 110 == brunch_event.reserved_spots
    assert 10 == brunch_event.over_reserved_spots

@pytest.mark.django_db
def test_wedding_concept_event_generation(faker): 
    wedding_concept = event_factories.WeddingConceptFactory.create()
    assert wedding_concept.generate_events()

@pytest.mark.django_db
def test_dinner_and_dance_concept_event_generation(faker): 
    dinner_and_dance_concept = event_factories.DinnerAndDanceConceptFactory.create()
    assert dinner_and_dance_concept.generate_events()



    

