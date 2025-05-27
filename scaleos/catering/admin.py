from admin_ordering.admin import OrderableAdmin
from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin
from polymorphic.admin import PolymorphicParentModelAdmin
from polymorphic.admin import StackedPolymorphicInline

from .models import Allergen
from .models import BreakfastMenu
from .models import BrunchMenu
from .models import Caterer
from .models import Catering
from .models import CateringDish
from .models import CateringMenu
from .models import CateringProduct
from .models import Course
from .models import DinnerMenu
from .models import Dish
from .models import DishImage
from .models import Ingredient
from .models import LunchMenu
from .models import Menu
from .models import Product
from .models import ProductImage
from .models import Recipe
from .models import RecipeIngredient


class CateringDishInlineAdmin(admin.TabularInline):
    model = CateringDish
    extra = 1
    show_change_link = True


class DishImageInlineAdmin(admin.TabularInline):
    model = DishImage
    extra = 1
    fields = ("image",)
    show_change_link = True


class ProductImageInlineAdmin(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image",)
    show_change_link = True


class RecipeInlineAdmin(admin.TabularInline):
    model = Recipe
    extra = 1
    fields = ("name",)
    show_change_link = True


class DishInlineAdmin(admin.TabularInline):
    model = Dish
    extra = 1
    fields = ("name",)
    show_change_link = True


class MenuInlineAdmin(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class BrunchMenuInlineAdmin(StackedPolymorphicInline.Child):
        model = BrunchMenu
        show_change_link = True

    class LunchMenuInlineAdmin(StackedPolymorphicInline.Child):
        model = LunchMenu
        show_change_link = True

    class DinnerMenuInlineAdmin(StackedPolymorphicInline.Child):
        model = DinnerMenu
        show_change_link = True

    class BreakfastMenuInlineAdmin(StackedPolymorphicInline.Child):
        model = BreakfastMenu
        show_change_link = True

    model = Menu
    child_inlines = (
        BreakfastMenuInlineAdmin,
        LunchMenuInlineAdmin,
        DinnerMenuInlineAdmin,
        BrunchMenuInlineAdmin,
    )


class CourseInline(admin.TabularInline):
    model = Course
    ordering_field = "ordering"
    extra = 1
    show_change_link = True


# ----------------------------
# Caterer Admin
# ----------------------------
@admin.register(Caterer)
class CatererAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    list_display = ("id", "name", "organization")
    search_fields = ("name",)
    inlines = [MenuInlineAdmin, DishInlineAdmin]


# ----------------------------
# Caterer Admin
# ----------------------------
@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "caterer", "image_count"]
    inlines = [DishImageInlineAdmin, RecipeInlineAdmin]


# ----------------------------
# Menu Admin (Polymorphic)
# ----------------------------


class MenuChildAdmin(PolymorphicChildModelAdmin):
    base_model = Menu
    show_in_index = True
    list_display = ("name", "caterer")


@admin.register(BrunchMenu)
class BrunchMenuAdmin(MenuChildAdmin):
    inlines = [CourseInline]


@admin.register(LunchMenu)
class LunchMenuAdmin(MenuChildAdmin):
    inlines = [CourseInline]


@admin.register(DinnerMenu)
class DinnerMenuAdmin(MenuChildAdmin):
    inlines = [CourseInline]


@admin.register(BreakfastMenu)
class BreakfastMenuAdmin(MenuChildAdmin):
    inlines = [CourseInline]


@admin.register(Menu)
class MenuParentAdmin(PolymorphicParentModelAdmin):
    base_model = Menu
    child_models = (BrunchMenu, DinnerMenu, BreakfastMenu, LunchMenu)
    list_display = ("name", "caterer")
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ("name",)
    inlines = [CourseInline]


# ----------------------------
# Course Admin (Polymorphic)
# ----------------------------


@admin.register(Course)
class CourseAdmin(OrderableAdmin, admin.ModelAdmin):
    ordering_field = "ordering"
    list_display = ("id", "ordering")
    ordering = ("menu", "ordering")
    search_fields = ("menu__name",)


# ----------------------------
# Allergen Admin
# ----------------------------


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "severity",
        "is_regulated_eu",
        "is_regulated_us",
        "icon_name",
    )
    list_filter = ("severity", "is_regulated_eu", "is_regulated_us")
    search_fields = ("name", "code")


# ----------------------------
# Product Admin
# ----------------------------


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("barcode", "name", "brand", "last_synced")
    search_fields = ("name", "barcode", "brand")
    list_filter = ("brand",)
    filter_horizontal = ("allergens", "traces")
    inlines = [ProductImageInlineAdmin]


# ----------------------------
# Ingredient Admin
# ----------------------------


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("products", "allergens")


# ----------------------------
# RecipeIngredient Inline
# ----------------------------


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


# ----------------------------
# Recipe Admin
# ----------------------------


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]


# ----------------------------
# CateringMenu Inline
# ----------------------------


class CateringMenuInlineAdmin(admin.TabularInline):
    model = CateringMenu
    extra = 1
    autocomplete_fields = ["menu"]
    show_change_link = True


# ----------------------------
# CateringProduct Inline
# ----------------------------


class CateringProductInlineAdmin(admin.TabularInline):
    model = CateringProduct
    extra = 1
    autocomplete_fields = ["product"]
    show_change_link = True


# ----------------------------
# Catering Admin
# ----------------------------


@admin.register(Catering)
class CateringAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ("id",)  # Or use a field like "name" if you have one
    inlines = [
        CateringMenuInlineAdmin,
        CateringProductInlineAdmin,
        CateringDishInlineAdmin,
    ]


@admin.register(CateringMenu)
class CateringMenuAdmin(admin.ModelAdmin):
    list_display = ("catering", "menu")
    search_fields = ("catering__id", "menu__name")
    autocomplete_fields = ["catering", "menu"]


@admin.register(CateringProduct)
class CateringProductAdmin(admin.ModelAdmin):
    list_display = ("catering", "product")
    search_fields = ("catering__id", "product__name")
    autocomplete_fields = ["catering", "product"]
