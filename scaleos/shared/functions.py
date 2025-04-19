import logging
import re
from datetime import datetime
from urllib.parse import urlparse

from dateutil.relativedelta import relativedelta
from disposable_email_domains import blocklist
from django.utils.translation import gettext_lazy as _
from email_validator import EmailNotValidError
from email_validator import validate_email

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
            date_object = datetime.strptime(birthday_string, fmt)  # noqa: DTZ007

            # Check for unlikely years (outside a reasonable range)
            if date_object.year > ITS_NOW.year or date_object.year < max_year:
                logger.debug("Unlikely birthday: %s", date_object)
                new_result = date_object - relativedelta(years=100)
                if new_result.year > ITS_NOW.year:
                    return None
                return new_result.strftime("%Y-%m-%d")

            result = date_object.strftime("%Y-%m-%d")  # YYYY-MM-DD
            logger.debug("Cleaned birthday: %s", result)

        except ValueError:
            pass  # Try the next format
        else:
            return result

    logger.debug("Invalid birthday format: %s", birthday_string)
    return None


def valid_email_address(email_address) -> tuple[bool, str]:  # noqa: PLR0911
    logger.debug("Validating email address: %s", email_address)

    if not isinstance(email_address, str):
        msg = _("email address must be a string")
        return False, msg

    if is_blank(email_address):
        msg = _("email address is required")
        return False, msg

    if not email_address:
        msg = _("email address is required")
        return False, msg

    min_email_length = 5
    if len(email_address) < min_email_length:
        msg = _(
            "email address '%(email)s' must be at least %(min_length)s characters long",
        ) % {
            "email": email_address,
            "min_length": min_email_length,
        }
        logger.info(msg)
        return False, msg

    try:
        # Check that the email address is valid. Turn on check_deliverability
        # for first-time validations like on account creation pages (but not
        # login pages).
        email_address = validate_email(
            email_address,
            check_deliverability=True,
        )

        # After this point, use only the normalized form of the email address,
        # especially before going to a database query.
        email_address = email_address.normalized

    except EmailNotValidError as e:
        # The exception message is human-readable explanation of why it's
        # not a valid (or deliverable) email address.
        logger.warning(e)
        return False, str(e)

    email_domain = email_address.split("@")[1]
    logger.debug("checking if email domain is blacklisted")
    if email_domain in blocklist:
        str_blacklisted = _("is blacklisted")
        msg = f"{email_address} {str_blacklisted}"
        logger.warning(msg)
        return False, msg

    logger.debug("email address is valid")

    return True, ""


def is_blank(value):
    logger.debug("Checking if value is blank: '%s'", value)
    value = str(value)
    result = not value or not value.strip()
    if result:
        logger.debug("Value is blank")
    else:
        logger.debug("Value is not blank")

    return result


def get_base_url_from_string(full_url: str) -> str:
    logger.debug("Trying to get the base url from %s", full_url)
    https_port = 443
    http_port = 80

    parsed = urlparse(full_url)

    scheme = parsed.scheme
    hostname = parsed.hostname
    port = parsed.port

    # Remove port if it's the default for the scheme
    if (
        (scheme == "http" and port == http_port)
        or (scheme == "https" and port == https_port)
        or port is None
    ):
        netloc = hostname
    else:
        netloc = f"{hostname}:{port}"

    return f"{scheme}://{netloc}"
