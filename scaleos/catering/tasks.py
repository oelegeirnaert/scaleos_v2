import logging

import requests
from django.db import transaction
from django.utils.timezone import now

from config import celery_app

from .models import Allergen
from .models import Dish
from .models import Ingredient
from .models import Product
from .models import Recipe
from .models import RecipeIngredient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@celery_app.task(bind=True, soft_time_limit=60 * 60, max_retries=3)
def sync_product_from_openfoodfacts(self, product_id):
    try:
        logger.debug("Syncing product %s from OpenFoodFacts", product_id)
        product = Product.objects.get(id=product_id)
        if not product.barcode:
            return

        url = f"https://world.openfoodfacts.org/api/v0/product/{product.barcode}.json"
        response = requests.get(url, timeout=30)
        data = response.json()

        if data.get("status") != 1:
            return  # Product not found

        product_data = data["product"]
        logger.debug(product_data)
        product.name = product_data.get("product_name", product.name)
        product.ingredients_text = product_data.get("ingredients_text", "")
        product.brand = product_data.get("brands", "")
        product.categories = product_data.get("categories", "")
        product.image_url = product_data.get("image_url", "")
        if product.image_url:
            from scaleos.files.tasks import download_file_from_url

            download_file_from_url.delay(
                product.image_url,
                related_ids={"product_id": product_id},
            )
        product.openfoodfacts_url = product_data.get("url", "")
        product.last_synced = now()

        # Save basic info first
        product.save()

        # Handle allergens
        allergen_tags = product_data.get("allergens_tags", [])
        trace_tags = product_data.get("traces_tags", [])

        for tag_list, field in [
            (allergen_tags, product.allergens),
            (trace_tags, product.traces),
        ]:
            field.clear()
            for tag in tag_list:
                name = tag.split(":")[-1].replace("_", " ").title()
                allergen, _ = Allergen.objects.get_or_create(name=name)
                field.add(allergen)

    except Product.DoesNotExist:
        pass
    except Exception as e:  # noqa: BLE001
        # Log error or retry as needed
        logger.info("Error syncing product %s: %s", product_id, e)


@celery_app.task(bind=True, soft_time_limit=60 * 60, max_retries=3)
def import_mealdb_dishes(self, search_query="Arrabiata"):
    logger.debug("Importing dishes from MealDB")
    try:
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={search_query}"
        logger.debug("URL: %s", url)
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        meals = data.get("meals", [])

        if not meals:
            msg = f"No meals found for search '{search_query}'"
            logger.warning(msg)
            return msg

        for meal in meals:
            with transaction.atomic():
                # Create or get Dish
                dish_name = meal["strMeal"]
                dish_description = meal.get("strInstructions", "")
                dish, _ = Dish.objects.get_or_create(
                    name=dish_name,
                    defaults={"description": dish_description},
                )
                dish_picture_url = meal.get("strMealThumb", "")
                if dish_picture_url:
                    from scaleos.files.tasks import download_file_from_url

                    download_file_from_url.delay(
                        dish_picture_url,
                        related_ids={"dish_id": dish.id},
                    )

                # Create Recipe
                recipe = Recipe.objects.create(
                    dish=dish,
                    name=f"{dish_name} Recipe",
                    instructions=meal.get("strInstructions", ""),
                )

                # Handle Ingredients and Quantities
                for i in range(1, 21):
                    ingredient_name = meal.get(f"strIngredient{i}")

                    quantity = meal.get(f"strMeasure{i}", "")
                    if quantity:
                        quantity = quantity.strip()

                    if ingredient_name and ingredient_name.strip():
                        ingredient_name = ingredient_name.strip()
                        ingredient, _ = Ingredient.objects.get_or_create(
                            name=ingredient_name,
                        )

                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            ingredient=ingredient,
                            quantity=quantity or "To taste",
                        )

        return f"Successfully imported {len(meals)} meals from TheMealDB"

    except requests.RequestException as re:
        raise self.retry(exc=re, countdown=10) from re
    except Exception as e:  # noqa: BLE001
        self.retry(exc=e, countdown=30)
