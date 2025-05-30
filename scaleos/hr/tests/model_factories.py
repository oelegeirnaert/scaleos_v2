import datetime

from factory import Faker
from factory import fuzzy
from factory.django import DjangoModelFactory

from scaleos.hr import models as hr_models


class PersonFactory(DjangoModelFactory[hr_models.Person]):
    primary_email_address = Faker("email")
    first_name = Faker("first_name")
    family_name = Faker("last_name")
    birthday = fuzzy.FuzzyDate(
        datetime.date(1960, 1, 1),
        datetime.date(2025, 12, 31),
    )

    class Meta:
        model = hr_models.Person
        django_get_or_create = ["primary_email_address"]
