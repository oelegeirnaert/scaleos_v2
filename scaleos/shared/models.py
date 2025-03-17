from django.db import models
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class CardModel(models.Model):
    def model_directory_path(self, filename):
        # file will be uploaded to MEDIA_ROOT / images / ...
        return f"images/{self.model_name}/{filename}"

    card_image = models.ImageField(  # noqa: DJ012
        _("card image"),
        upload_to=model_directory_path,
        null=True,
        blank=True,
    )
    card_description = models.TextField(_("card description"), default="", blank=True)

    class Meta:  # noqa: DJ012
        abstract = True

    @cached_property
    def card_template(self):
        return f"{self.app_label}/{self.model_name}/card.html"

    @cached_property
    def page_url(self):
        try:
            the_url = reverse(
                f"{self.app_label}:{self.model_name}",
                kwargs={f"{self.model_name}_slug": self.slug},
            )
            return f"href={the_url}"  # noqa: TRY300
        except NoReverseMatch:
            pass

        return ""

    def card_image_url(self):
        """
        should be card 'card_image_url'
        because the actual model can also have an image
        """
        if self.card_image:
            return self.card_image.url  # pragma: no cover
        if hasattr(self, "CARD_IMAGE"):
            return self.CARD_IMAGE

        return None
