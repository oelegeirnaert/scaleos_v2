from factory.django import DjangoModelFactory

from scaleos.stores import models as store_models


class StoreFactory(DjangoModelFactory[store_models.Store]):
    class Meta:
        model = store_models.Store


class PurchasableItemFactory(DjangoModelFactory[store_models.PurchasableItem]):
    class Meta:
        model = store_models.PurchasableItem


class ProductFactory(DjangoModelFactory[store_models.Product]):
    class Meta:
        model = store_models.Product


class ServiceFactory(DjangoModelFactory[store_models.Service]):
    class Meta:
        model = store_models.Service
