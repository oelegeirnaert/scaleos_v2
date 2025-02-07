from django.test import TestCase
from scaleos.events import models as event_models
from scaleos.events.tests import model_factories
import pytest
from uuid import uuid4
import logging
import datetime
from moneyed import Money, EUR, USD
from django.utils import timezone

@pytest.mark.django_db
def test_brunchconcept_can_generate_events(faker): 
    brunch_concept = model_factories.BrunchConceptFactory.create()
    from_date = datetime.date(year=2025, month=2, day=1)
    to_date = datetime.date(year=2025, month=3, day=1)
    weekday = 7
    brunch_concept.generate(from_date, to_date, weekday)
    assert 4 == brunch_concept.events.count(), "4 sundays in feb 2025"

@pytest.mark.django_db
def test_brunch_has_free_capacity(faker): 
    brunch_event = model_factories.BrunchEventFactory.create()
    brunch_event.maximum_number_of_guests = 100
    assert 100 == brunch_event.free_spots
    assert 100 == brunch_event.free_percentage

