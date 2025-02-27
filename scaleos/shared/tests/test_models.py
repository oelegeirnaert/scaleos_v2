from django.test import TestCase

from scaleos.shared import models as shared_models


class TestCardModel(TestCase):
    def setUp(self):
        # Create a dummy model that inherits from CardModel
        class MyCard(shared_models.CardModel):
            app_label = "myapp"
            model_name = "mycard"
            CARD_IMAGE = "/path/to/default/image.jpg"

        self.MyCard = MyCard

    def test_model_directory_path(self):
        card = self.MyCard()
        filename = "test_image.jpg"
        expected_path = f"images/{card.model_name}/{filename}"
        assert card.model_directory_path(filename) == expected_path

    def test_card_template(self):
        card = self.MyCard()
        expected_template = f"{card.app_label}/{card.model_name}/card.html"
        assert card.card_template == expected_template

    def test_card_image_url_with_default_image(self):
        card = self.MyCard()
        expected_url = card.CARD_IMAGE
        assert card.card_image_url() == expected_url

    def test_card_image_url_no_image(self):
        # Create a dummy model that inherits from CardModel
        class MyCard2(shared_models.CardModel):
            app_label = "myapp"
            model_name = "mycard2"

        card = MyCard2()
        assert card.card_image_url() is None
