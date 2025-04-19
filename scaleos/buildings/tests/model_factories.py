from factory.django import DjangoModelFactory

from scaleos.buildings import models as building_models


class RoomFactory(DjangoModelFactory[building_models.Room]):
    class Meta:
        model = building_models.Room


class TerraceFactory(DjangoModelFactory[building_models.Terrace]):
    class Meta:
        model = building_models.Terrace


class BuildingFactory(DjangoModelFactory[building_models.Building]):
    class Meta:
        model = building_models.Building


class FloorFactory(DjangoModelFactory[building_models.Floor]):
    class Meta:
        model = building_models.Floor
