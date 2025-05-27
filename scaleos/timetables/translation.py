from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from scaleos.timetables import models as timetable_models


class PublicHolidayTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(timetable_models.PublicHoliday, PublicHolidayTranslationOptions)
