from factory.django import DjangoModelFactory

from scaleos.geography import models as geography_models


class AddressFactory(DjangoModelFactory[geography_models.Address]):
    class Meta:
        model = geography_models.Address
