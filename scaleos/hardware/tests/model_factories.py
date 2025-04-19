from factory.django import DjangoModelFactory

from scaleos.hardware import models as hardware_models


class NetworkFactory(DjangoModelFactory[hardware_models.Network]):
    class Meta:
        model = hardware_models.Network


class DeviceFactory(DjangoModelFactory[hardware_models.Device]):
    class Meta:
        model = hardware_models.Device


class ComputerFactory(DjangoModelFactory[hardware_models.Computer]):
    class Meta:
        model = hardware_models.Computer
