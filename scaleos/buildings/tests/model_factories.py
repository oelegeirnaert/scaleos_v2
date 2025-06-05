from factory.django import DjangoModelFactory

from scaleos.buildings import models as building_models


class RoomFactory(DjangoModelFactory[building_models.Room]):
    class Meta:
        model = building_models.Room

class BedRoomFactory(DjangoModelFactory[building_models.BedRoom]):
    class Meta:
        model = building_models.BedRoom

class BathRoomFactory(DjangoModelFactory[building_models.BathRoom]):
    class Meta:
        model = building_models.BathRoom

class PartyFactory(DjangoModelFactory[building_models.Party]):
    class Meta:
        model = building_models.Party


class PersonFactory(DjangoModelFactory[building_models.Person]):
    class Meta:
        model = building_models.Person


class OrganizationFactory(DjangoModelFactory[building_models.Organization]):
    class Meta:
        model = building_models.Organization


class LivingRoomFactory(DjangoModelFactory[building_models.LivingRoom]):
    class Meta:
        model = building_models.LivingRoom


class KitchenFactory(DjangoModelFactory[building_models.Kitchen]):
    class Meta:
        model = building_models.Kitchen





class TerraceFactory(DjangoModelFactory[building_models.Terrace]):
    class Meta:
        model = building_models.Terrace


class BuildingFactory(DjangoModelFactory[building_models.Building]):
    class Meta:
        model = building_models.Building


class FloorFactory(DjangoModelFactory[building_models.Floor]):
    class Meta:
        model = building_models.Floor
