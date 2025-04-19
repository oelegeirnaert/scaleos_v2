from factory.django import DjangoModelFactory

from scaleos.software import models as software_models


class ServiceFactory(DjangoModelFactory[software_models.Service]):
    class Meta:
        model = software_models.Service


class OllamaServiceFactory(DjangoModelFactory[software_models.OllamaService]):
    class Meta:
        model = software_models.OllamaService
