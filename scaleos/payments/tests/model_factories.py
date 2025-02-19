from factory.django import DjangoModelFactory

from scaleos.payments import models as payment_models


class PriceMatrixFactory(DjangoModelFactory[payment_models.PriceMatrix]):
    class Meta:
        model = payment_models.PriceMatrix


class AgePriceMatrixItemFactory(DjangoModelFactory[payment_models.AgePriceMatrixItem]):
    class Meta:
        model = payment_models.AgePriceMatrixItem


class AgePriceMatrixFactory(DjangoModelFactory[payment_models.AgePriceMatrix]):
    class Meta:
        model = payment_models.AgePriceMatrix


class PriceFactory(DjangoModelFactory[payment_models.Price]):
    class Meta:
        model = payment_models.Price
