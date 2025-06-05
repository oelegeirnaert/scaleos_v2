from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from scaleos.buildings import models as building_models


class FloorTranslationOptions(TranslationOptions):
    fields = ("name", "card_description")


translator.register(building_models.Floor, FloorTranslationOptions)






class TerraceTranslationOptions(TranslationOptions):
    pass


translator.register(building_models.Terrace, TerraceTranslationOptions)





class BuildingTranslationOptions(TranslationOptions):
    pass


translator.register(building_models.Building, BuildingTranslationOptions)


class RoomTranslationOptions(TranslationOptions):
    pass


translator.register(building_models.Room, RoomTranslationOptions)







class BedRoomTranslationOptions(TranslationOptions):
    pass


translator.register(building_models.BedRoom, BedRoomTranslationOptions)

class BathRoomTranslationOptions(TranslationOptions):
    pass


translator.register(building_models.BathRoom, BathRoomTranslationOptions)



