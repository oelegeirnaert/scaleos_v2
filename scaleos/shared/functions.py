import logging
import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from scaleos.shared.mixins import ITS_NOW

logger = logging.getLogger(__name__)


def mobile_phone_number_cleaning(phone_number, country_prefix="32"):
    """
    Cleans and standardizes mobile phone numbers to the international format (E.164).

    Args:
        phone_number (str): The mobile phone number to clean.

    Returns:
        str: The cleaned phone number in international format (E.164) if valid,
             otherwise returns None.

    Examples:
        >>> mobile_phone_number_cleaning("+32-0485517786")
        '+32485517786'
        >>> mobile_phone_number_cleaning("0485517786")
        '+32485517786'
        >>> mobile_phone_number_cleaning("0485 51 77 86")
        '+32485517786'
        >>> mobile_phone_number_cleaning("+32485517786")
        '+32485517786'
        >>> mobile_phone_number_cleaning("32485517786")
        '+32485517786'
        >>> mobile_phone_number_cleaning("+1-555-123-4567")
        '+15551234567'
        >>> mobile_phone_number_cleaning("555-123-4567")
        None
        >>> mobile_phone_number_cleaning("5551234567")
        None

    """
    if not isinstance(phone_number, str):
        return None

    # Remove all non-digit characters except for the leading '+'
    cleaned_number = re.sub(r"[^\d+]", "", phone_number)

    miminum_digits = 9
    if len(cleaned_number) < miminum_digits:
        return None

    return f"+{country_prefix}{cleaned_number[-miminum_digits:]}"


def birthday_cleaning(birthday_string):
    logger.setLevel(logging.DEBUG)
    """
    Cleans and standardizes birthday strings to a consistent YYYY-MM-DD format.

    Args:
        birthday_string (str): The birthday string in various formats.

    Returns:
        str: The cleaned birthday in YYYY-MM-DD format if valid, otherwise None.

    Examples:
        >>> birthday_cleaning("11/8/1961")
        '1961-11-08'
        >>> birthday_cleaning("5/30/63 1:00")
        '1963-05-30'
        >>> birthday_cleaning("3/31/1950")
        '1950-03-31'
        >>> birthday_cleaning("4/19/67 1:00")
        '1967-04-19'
        >>> birthday_cleaning("10/7/9953")
        None
        >>> birthday_cleaning("10/22/72 1:00")
        '1972-10-22'
        >>> birthday_cleaning("invalid date")
        None
    """
    max_year = 1900
    if not isinstance(birthday_string, str):
        return None

    birthday_string = birthday_string.strip()

    # Try different formats
    formats_to_try = [
        "%m/%d/%Y",  # MM/DD/YYYY
        "%m/%d/%y %H:%M",  # MM/DD/YY HH:MM
        "%m/%d/%y",  # MM/DD/YY
        "%m/%d/%Y %H:%M",  # MM/DD/YYYY HH:MM
    ]

    for fmt in formats_to_try:
        logger.debug("Trying format: %s", fmt)
        try:
            date_object = datetime.strptime(birthday_string, fmt).replace(
                tzinfo=datetime.timezone.utc,
            )

            # Check for unlikely years (outside a reasonable range)
            if date_object.year > ITS_NOW.year or date_object.year < max_year:
                logger.debug("Unlikely birthday: %s", date_object)
                new_result = date_object - relativedelta(years=100)
                if new_result.year > ITS_NOW.year:
                    return None
                return new_result.strftime("%Y-%m-%d")

            result = date_object.strftime("%Y-%m-%d")  # YYYY-MM-DD
            logger.debug("Cleaned birthday: %s", result)
            return result  # noqa: TRY300
        except ValueError:
            pass  # Try the next format

    logger.debug("Invalid birthday format: %s", birthday_string)
    return None
