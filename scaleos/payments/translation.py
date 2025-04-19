from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from scaleos.payments import models as payment_models


class PriceMatrixItemTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(payment_models.PriceMatrixItem, PriceMatrixItemTranslationOptions)


class PriceMatrixItemTranslationOptions(TranslationOptions):
    pass


translator.register(
    payment_models.AgePriceMatrixItem,
    PriceMatrixItemTranslationOptions,
)


class BulkPriceMatrixItemTranslationOptions(TranslationOptions):
    pass


translator.register(
    payment_models.BulkPriceMatrixItem,
    BulkPriceMatrixItemTranslationOptions,
)
