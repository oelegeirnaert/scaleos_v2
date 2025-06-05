import calendar
import datetime
import logging
from datetime import date
from datetime import timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

from django.utils import timezone
from geopy.exc import GeocoderServiceError
from geopy.exc import GeocoderTimedOut
from geopy.exc import GeocoderUnavailable
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

logger = logging.getLogger(__name__)


def get_current_year():
    logger.debug("Getting current year")
    current_year = timezone.localtime().year
    logger.debug("Found current year %s", current_year)
    return current_year


def get_current_month():
    logger.debug("Getting current month")
    current_month = timezone.localtime().month
    logger.debug("Found current month %s", current_month)
    return current_month


def get_current_week():
    logger.debug("Getting current week")
    current_week = timezone.localtime().isocalendar()[1]
    logger.debug("Found current week %s", current_week)
    return current_week


def get_current_weekday():
    logger.debug("Getting current weekday")
    current_weekday = timezone.localtime().weekday()
    logger.debug("Found current weekday %s", current_weekday)
    return current_weekday


def get_current_day():
    logger.debug("Getting current day")
    current_day = timezone.localtime().isocalendar()[2]
    logger.debug("Found current day %s", current_day)
    return current_day


def get_days_in_a_year(year):
    logger.debug("Getting days in year %s", year)
    return 366 if calendar.isleap(year) else 365


def get_date_by_day_of_year(day_number, year):
    logger.debug("Getting date by day of year %s and year %s", day_number, year)
    return date(year, 1, 1) + timedelta(day_number - 1)


def get_weeks_in_year(year):
    logger.debug("Getting weeks in year %s", year)
    # December 28th is always in the last ISO week of the year
    dec_28 = date(year, 12, 28)
    number_of_weeks = dec_28.isocalendar()[1]
    logger.debug("Found %s weeks in year %s", number_of_weeks, year)
    return number_of_weeks


def get_date_of_next(weekday_name: str) -> datetime.date:
    # Normalize and map weekday name to weekday number
    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    weekday_name = weekday_name.capitalize()

    if weekday_name not in weekdays:
        msg = f"Invalid weekday name: {weekday_name}"
        raise ValueError(msg)

    target_weekday = weekdays.index(weekday_name)
    today = timezone.now().today()
    today_weekday = today.weekday()

    # Calculate days until next target weekday
    days_ahead = (target_weekday - today_weekday + 7) % 7
    days_ahead = days_ahead or 7  # If today is the target, return next week's

    return today + datetime.timedelta(days=days_ahead)


geolocator = Nominatim(user_agent="scaleos.net")
tf = TimezoneFinder()


@lru_cache(maxsize=256)
def get_timezone_from_country(country_name: str) -> ZoneInfo:
    """
    Returns a timezone for the given country name using geolocation.
    """
    try:
        location = geolocator.geocode(country_name)
        if location:
            tz_name = tf.timezone_at(lat=location.latitude, lng=location.longitude)
            if tz_name:
                return ZoneInfo(tz_name)
    except (
        GeocoderTimedOut,
        GeocoderUnavailable,
        GeocoderServiceError,
        AttributeError,
        ValueError,
    ) as e:
        logger.info("Failed to determine timezone for %s: %s", country_name, e)
    return ZoneInfo("UTC")
