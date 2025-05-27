# Create your models here.
import logging

from admin_ordering.models import OrderableModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.fields import SegmentField
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.shared.models import CardModel

logger = logging.getLogger("scaleos")


class CateringField(models.Model):
    catering = models.ForeignKey(
        "catering.Catering",
        verbose_name=_(
            "catering",
        ),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class Caterer(AdminLinkMixin, SegmentField, PublicKeyField, NameField):
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="caterers",
        verbose_name=_("organization"),
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )

    class Meta:
        verbose_name = _("caterer")
        verbose_name_plural = _("caterers")

    def __str__(self):
        if (
            self.organization
            and hasattr(self.organization, "name")
            and self.organization.name
        ):
            return f"{self.organization.name}"

        return super().__str__()


class Menu(PolymorphicModel, NameField, CardModel, LogInfoFields, AdminLinkMixin):
    caterer = models.ForeignKey(Caterer, related_name="menus", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("menu")
        verbose_name_plural = _("menus")

    @property
    def images(self):
        dish_ids = self.courses.all().values_list("dish_id", flat=True)
        return DishImage.objects.filter(dish_id__in=dish_ids)


class BrunchMenu(Menu):
    special_note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _("brunch menu")
        verbose_name_plural = _("brunch menus")


class LunchMenu(Menu):
    special_note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _("lunch menu")
        verbose_name_plural = _("lunch menus")


class DinnerMenu(Menu):
    wine_pairing_available = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("dinner menu")
        verbose_name_plural = _("dinner menus")


class BreakfastMenu(Menu):
    includes_coffee = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("breakfast menu")
        verbose_name_plural = _("breakfast menus")


class Course(OrderableModel):
    class CourseType(models.TextChoices):
        AMUSE_BOUCHE = "AMUSE_BOUCHE", _("amuse-bouche")
        STARTER = "STARTER", _("starter")
        SOUP = "SOUP", _("soup")
        SALAD = "SALAD", _("salad")
        FISH = "FISH", _("fish")
        MAIN = "MAIN", _("main")
        CHEESE = "CHEESE", _("cheese")
        DESSERT = "DESSERT", _("dessert")
        DRINK = "DRINK", _("drink")
        DIGESTIF = "DIGESTIF", _("digestif")
        OTHER = "OTHER", _("other")
        APPETIZER = "APPETIZER", _("appetizer")

    menu = models.ForeignKey("Menu", related_name="courses", on_delete=models.CASCADE)
    course_type = models.CharField(
        verbose_name=_(
            "course type",
        ),
        max_length=50,
        choices=CourseType.choices,
        help_text=_("who do we need to inform"),
        default="",
        blank=True,
    )
    dish = models.ForeignKey(
        "Dish",
        related_name="courses",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta(OrderableModel.Meta):
        verbose_name = _("course")
        verbose_name_plural = _("courses")


class Allergen(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", _("low")
        MODERATE = "MODERATE", _("moderate")
        HIGH = "HIGH", _("high")

    name = models.CharField(max_length=100, default="")
    code = models.CharField(
        max_length=10,
        blank=True,
        help_text="Optional code, e.g. 'A01'",
    )
    severity = models.CharField(
        verbose_name=_(
            "inform",
        ),
        max_length=50,
        choices=Severity.choices,
        help_text=_("who do we need to inform"),
        default=Severity.MODERATE,
        blank=True,
    )
    description = models.TextField(blank=True)
    is_regulated_eu = models.BooleanField(default=False)
    is_regulated_us = models.BooleanField(default=False)
    icon_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Lucide icon name, e.g. 'egg', 'milk', 'fish'",
    )

    def __str__(self):
        return self.name


class Product(AdminLinkMixin, CardModel):
    barcode = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255, default="", blank=True)
    ingredients_text = models.TextField(blank=True)
    allergens = models.ManyToManyField("Allergen", blank=True)
    traces = models.ManyToManyField(
        "Allergen",
        related_name="trace_products",
        blank=True,
    )

    # OpenFoodFacts specific metadata
    brand = models.CharField(max_length=100, blank=True)
    categories = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    openfoodfacts_url = models.URLField(blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.barcode})"


class ProductImage(AdminLinkMixin):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ForeignKey(
        "files.ImageFile",
        related_name="product_images",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("dish image")
        verbose_name_plural = _("dish images")


class Ingredient(models.Model):
    name = models.CharField(max_length=100, default="")
    products = models.ManyToManyField(Product, blank=True)
    allergens = models.ManyToManyField(Allergen, related_name="ingredients", blank=True)

    def __str__(self):
        return self.name


class Dish(CardModel, AdminLinkMixin):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    caterer = models.ForeignKey(
        Caterer,
        related_name="dishes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("dish")
        verbose_name_plural = _("dishes")

    def __str__(self):
        return self.name

    @property
    def image_count(self):
        return self.images.count()


class DishImage(AdminLinkMixin):
    dish = models.ForeignKey(Dish, related_name="images", on_delete=models.CASCADE)
    image = models.ForeignKey(
        "files.ImageFile",
        related_name="dish_images",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("dish image")
        verbose_name_plural = _("dish images")


class Recipe(AdminLinkMixin):
    dish = models.ForeignKey(
        Dish,
        related_name="recipes",
        on_delete=models.CASCADE,
        null=True,
    )
    name = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    ingredients = models.ManyToManyField(Ingredient, through="RecipeIngredient")

    class Meta:
        verbose_name = _("recipe")
        verbose_name_plural = _("recipes")

    def __str__(self):
        return self.name

    @property
    def allergens(self):
        return Allergen.objects.filter(
            ingredients__recipeingredient__recipe=self,
        ).distinct()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="recipe_ingredients",
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50)  # e.g., "2 tbsp", "100g"

    def __str__(self):
        return f"{self.quantity} of {self.ingredient.name} in {self.recipe.name}"


class Catering(AdminLinkMixin, PublicKeyField):
    @property
    def has_dinner_menu(self):
        return DinnerMenu.objects.filter(caterings__catering=self).exists()

    @property
    def has_lunch_menu(self):
        return LunchMenu.objects.filter(caterings__catering=self).exists()

    @property
    def has_breakfast_menu(self):
        return BreakfastMenu.objects.filter(caterings__catering=self).exists()

    @property
    def has_brunch_menu(self):
        return BrunchMenu.objects.filter(caterings__catering=self).exists()

    class Meta:
        verbose_name = _("catering")
        verbose_name_plural = _("caterings")

    @property
    def public_menus(self):
        return Menu.objects.filter(caterings__catering_id=self.pk)

    @property
    def public_dishes(self):
        return Dish.objects.filter(caterings__catering_id=self.pk)

    @property
    def public_products(self):
        return Product.objects.filter(caterings__catering_id=self.pk)


class CateringMenu(AdminLinkMixin):
    catering = models.ForeignKey(
        Catering,
        related_name="menus",
        on_delete=models.CASCADE,
    )
    menu = models.ForeignKey(Menu, related_name="caterings", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("catering menu")
        verbose_name_plural = _("catering menus")


class CateringDish(AdminLinkMixin):
    catering = models.ForeignKey(
        Catering,
        related_name="dishes",
        on_delete=models.CASCADE,
    )
    dish = models.ForeignKey(Dish, related_name="caterings", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("catering dish")
        verbose_name_plural = _("catering dishes")


class CateringProduct(AdminLinkMixin):
    catering = models.ForeignKey(
        Catering,
        related_name="products",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name="caterings",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("catering product")
        verbose_name_plural = _("catering products")
