from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from scaleos.geography import models as geography_models


class FloorTranslationOptions(TranslationOptions):
    fields = ("name", "card_description")


translator.register(geography_models.Floor, FloorTranslationOptions)


class BuildingTranslationOptions(TranslationOptions):
    pass


translator.register(geography_models.Building, BuildingTranslationOptions)


class RoomTranslationOptions(TranslationOptions):
    pass


translator.register(geography_models.Room, RoomTranslationOptions)
