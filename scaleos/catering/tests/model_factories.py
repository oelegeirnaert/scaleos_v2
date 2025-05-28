import factory
from factory import LazyFunction
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker as BaseFaker
from faker_food import FoodProvider

from scaleos.catering import models as catering_models
from scaleos.organizations.tests.model_factories import OrganizationFactory

fake = BaseFaker()
fake.add_provider(FoodProvider)


def generate_ean13():
    base = [str(factory.random.randgen.randint(0, 9)) for _ in range(12)]
    digits = list(map(int, base))
    # Calculate EAN-13 checksum
    checksum = (
        10 - (sum(digits[-1::-2]) + sum(d * 3 for d in digits[-2::-2])) % 10
    ) % 10
    return "".join(base) + str(checksum)


class CatererFactory(DjangoModelFactory[catering_models.Caterer]):
    class Meta:
        model = catering_models.Caterer

    organization = SubFactory(OrganizationFactory)


class CateringFactory(DjangoModelFactory[catering_models.Catering]):
    class Meta:
        model = catering_models.Catering


class MenuFactory(DjangoModelFactory[catering_models.Menu]):
    class Meta:
        model = catering_models.Menu

    caterer = SubFactory(CatererFactory)


class DishFactory(DjangoModelFactory[catering_models.Dish]):
    class Meta:
        model = catering_models.Dish

    caterer = SubFactory(CatererFactory)
    name = LazyFunction(lambda: fake.dish())


class CateringMenuFactory(DjangoModelFactory[catering_models.CateringMenu]):
    class Meta:
        model = catering_models.CateringMenu

    catering = SubFactory(CateringFactory)
    menu = SubFactory(MenuFactory)


class BrunchMenuFactory(MenuFactory):
    class Meta:
        model = catering_models.BrunchMenu


class DinnerMenuFactory(MenuFactory):
    class Meta:
        model = catering_models.DinnerMenu


class BreakfastMenuFactory(MenuFactory):
    class Meta:
        model = catering_models.BreakfastMenu


class LunchMenuFactory(MenuFactory):
    class Meta:
        model = catering_models.LunchMenu


class CourseFactory(DjangoModelFactory[catering_models.Course]):
    class Meta:
        model = catering_models.Course

    menu = SubFactory(MenuFactory)


class AllergenFactory(DjangoModelFactory[catering_models.Allergen]):
    class Meta:
        model = catering_models.Allergen


class ProductFactory(DjangoModelFactory[catering_models.Product]):
    class Meta:
        model = catering_models.Product

    barcode = factory.LazyFunction(generate_ean13)


class IngredientFactory(DjangoModelFactory[catering_models.Ingredient]):
    class Meta:
        model = catering_models.Ingredient


class RecipeFactory(DjangoModelFactory[catering_models.Recipe]):
    class Meta:
        model = catering_models.Recipe

    dish = SubFactory(DishFactory)


class RecipeIngredientFactory(DjangoModelFactory[catering_models.RecipeIngredient]):
    class Meta:
        model = catering_models.RecipeIngredient

    recipe = SubFactory(RecipeFactory)
    ingredient = SubFactory(IngredientFactory)


class CateringProductFactory(DjangoModelFactory[catering_models.CateringProduct]):
    class Meta:
        model = catering_models.CateringProduct

    catering = SubFactory(CateringFactory)
    product = SubFactory(ProductFactory)


class CateringDishFactory(DjangoModelFactory[catering_models.CateringDish]):
    class Meta:
        model = catering_models.CateringDish

    catering = SubFactory(CateringFactory)
    dish = SubFactory(DishFactory)
