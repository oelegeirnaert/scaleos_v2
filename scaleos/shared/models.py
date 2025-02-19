from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


def model_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT / images / ...
    return f"images/{instance.model_name}/{filename}"


class CardModel(models.Model):
    card_image = models.ImageField(
        _("card image"),
        upload_to=model_directory_path,
        null=True,
    )
    card_description = models.TextField(_("card description"), default="")

    class Meta:
        abstract = True

    @cached_property
    def card_template(self):
        return f"{self.app_label}/{self.model_name}/card.html"

    def card_image_url(self):
        """
        should be card 'card_image_url'
        because the actual model can also have an image
        """
        if self.card_image:
            return self.card_image.url
        if hasattr(self, "CARD_IMAGE"):
            return self.CARD_IMAGE

        return None
