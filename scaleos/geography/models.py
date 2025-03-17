import logging

import requests
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from scaleos.shared.fields import LogInfoFields
from scaleos.shared.mixins import AdminLinkMixin

logger = logging.getLogger(__name__)


# Create your models here.
class GPSFields(models.Model):
    gps_point = models.PointField(null=True, blank=True)
    gps_address = models.CharField(null=True, editable=False)

    class Meta:
        abstract = True

    def set_gps_point_from_address(self):
        logger.setLevel(logging.DEBUG)
        timeout_in_seconds = 10
        logger.debug("Getting a GPS point from address...")

        if not hasattr(self, "get_full_address"):  # pragma: no cover
            logger.info("We cannot get the full address")
            return False

        the_address = self.get_full_address(with_country=False)
        if the_address is None:
            logger.debug("We don't have an address")
            return False

        if self.gps_address == the_address:
            logger.debug("The address hasn't changed")
            return False

        response = requests.get(
            f"https://geo.api.vlaanderen.be/geolocation/v4/Location?q={the_address}",
            timeout=timeout_in_seconds,
        )
        if response.ok:
            logger.debug("Okay, we have a response: %s", response.text)
            json_result = response.json()["LocationResult"]
            if len(json_result) == 1:
                logger.debug("Okay, exactly one address...")
                json_result = json_result[0]
                logger.debug(json_result)
                lat = float(json_result["Location"]["Lat_WGS84"])
                lng = float(json_result["Location"]["Lon_WGS84"])
                pnt = Point(lng, lat)
                self.gps_point = pnt
                self.gps_address = the_address
                self.save()
                logger.info("GPS Point set!")
                return True

        return False  # pragma: no cover


class Address(GPSFields, LogInfoFields, AdminLinkMixin):
    street = models.CharField(default="", blank=True)
    house_number = models.CharField(default="", blank=True)
    bus = models.CharField(default="", blank=True)
    postal_code = models.CharField(default="", blank=True)
    city = models.CharField(default="", blank=True)
    country = CountryField(verbose_name=_("country"), null=True, blank=True)

    def get_full_address(self, *, with_country=True):
        if (
            self.street
            and self.house_number
            and self.bus
            and self.postal_code
            and self.city
            and with_country
            and self.country
        ):
            return f"{self.street} {self.house_number} {self.bus}, {self.postal_code} {self.city} {self.get_country_display()}"  # noqa: E501

        if (
            self.street
            and self.house_number
            and self.bus
            and self.postal_code
            and self.city
        ):
            return f"{self.street} {self.house_number} {self.bus}, {self.postal_code} {self.city}"  # noqa: E501

        if (
            self.street
            and self.house_number
            and self.postal_code
            and self.city
            and with_country
            and self.country
        ):
            return f"{self.street} {self.house_number}, {self.postal_code} {self.city} {self.get_country_display()}"  # noqa: E501

        if self.street and self.house_number and self.postal_code and self.city:
            return f"{self.street} {self.house_number}, {self.postal_code} {self.city}"

        if self.street and self.postal_code and self.city:
            return f"{self.street}, {self.postal_code} {self.city}"

        return None

    def __str__(self):
        the_address = self.get_full_address(with_country=True)
        if the_address:
            return the_address
        return super().__str__()

    @property
    def needs_correction(self):
        if self.modified_by:
            return False

        return len(self.house_number) == 0
