import ipaddress

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from scaleos.shared.functions import birthday_cleaning
from scaleos.shared.functions import get_client_ip
from scaleos.shared.functions import mobile_phone_number_cleaning
from scaleos.shared.functions import valid_email_address


class TestMobilePhoneNumberCleaning:
    def test_valid_international_format(self):
        assert mobile_phone_number_cleaning("+32-0324476509992") == "+32476509992"
        assert mobile_phone_number_cleaning("+32-0485517786") == "+32485517786"
        assert mobile_phone_number_cleaning("+32485517786") == "+32485517786"
        assert mobile_phone_number_cleaning("+32 485 51 77 86") == "+32485517786"
        assert mobile_phone_number_cleaning("320485517786") == "+32485517786"
        assert mobile_phone_number_cleaning("32-0485517786") == "+32485517786"

    def test_valid_belgium_format(self):
        assert mobile_phone_number_cleaning("0485517786") == "+32485517786"
        assert mobile_phone_number_cleaning("485517786") == "+32485517786"
        assert mobile_phone_number_cleaning("0485 51 77 86") == "+32485517786"
        assert mobile_phone_number_cleaning("0485-517786") == "+32485517786"
        assert mobile_phone_number_cleaning("0485.51.77.86") == "+32485517786"

    def test_invalid_formats(self):
        assert mobile_phone_number_cleaning("54") is None

    def test_not_a_string(self):
        assert mobile_phone_number_cleaning(12345) is None
        assert mobile_phone_number_cleaning(None) is None
        assert mobile_phone_number_cleaning({}) is None


class TestBirthdayCleaning:
    def test_valid_formats(self):
        assert birthday_cleaning("11/8/1961") == "1961-11-08"
        assert birthday_cleaning("5/30/63 1:00") == "1963-05-30"
        assert birthday_cleaning("3/31/1950") == "1950-03-31"
        assert birthday_cleaning("4/19/67 1:00") == "1967-04-19"
        assert birthday_cleaning("10/22/72 1:00") == "1972-10-22"
        assert birthday_cleaning(" 10/22/72 1:00 ") == "1972-10-22"
        assert birthday_cleaning("5/30/63") == "1963-05-30"
        assert birthday_cleaning("11/08/1961 1:00") == "1961-11-08"

    def test_invalid_formats(self):
        assert birthday_cleaning("10/7/9953") is None
        assert birthday_cleaning("invalid date") is None

    def test_not_a_string(self):
        assert birthday_cleaning(12345) is None
        assert birthday_cleaning(None) is None
        assert birthday_cleaning({}) is None


class TestValidEmailAddress:
    def test_valid_email_addresses(self):
        is_valid, msg = valid_email_address(None)
        assert is_valid is False
        assert msg == "email address must be a string"
        is_valid, msg = valid_email_address("")
        assert is_valid is False
        assert msg == "email address is required"
        is_valid, msg = valid_email_address(" ")
        assert is_valid is False
        assert msg == "email address is required"
        is_valid, msg = valid_email_address("a")
        assert is_valid is False
        assert msg == "email address 'a' must be at least 5 characters long"
        is_valid, msg = valid_email_address("a@b.c")
        assert is_valid is False
        assert msg == "The domain name b.c does not exist."
        is_valid, msg = valid_email_address("a@b.c.")
        assert is_valid is False
        assert msg == "An email address cannot end with a period."
        is_valid, msg = valid_email_address("oelegeirnaert@yopmail.com")
        assert is_valid is False
        assert msg == "oelegeirnaert@yopmail.com is blacklisted"
        is_valid, msg = valid_email_address("oelegeirnaert@hotmail.com")
        assert is_valid is True
        assert msg == ""


@pytest.fixture
def factory():
    return RequestFactory()


def test_get_client_ip_from_remote_addr(factory):
    request = factory.get("/")
    request.user = AnonymousUser()
    request.META["REMOTE_ADDR"] = "192.168.1.1"

    ip = get_client_ip(request)
    assert ip == "192.168.1.1"


def test_get_client_ip_from_x_forwarded_for(factory):
    request = factory.get("/")
    request.user = AnonymousUser()
    request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.42, 70.41.3.18, 150.172.238.178"
    request.META["REMOTE_ADDR"] = "192.168.1.1"  # should be ignored

    ip = get_client_ip(request)
    assert ip == "203.0.113.42"


def test_get_client_ip_with_single_forwarded_ip(factory):
    request = factory.get("/")
    request.META["HTTP_X_FORWARDED_FOR"] = "8.8.8.8"
    ip = get_client_ip(request)
    assert ip == "8.8.8.8"


def test_get_client_ip_defaults_to_remote_addr(factory):
    request = factory.get("/")
    # No HTTP_X_FORWARDED_FOR set, but REMOTE_ADDR will default to 127.0.0.1
    ip = get_client_ip(request)
    assert ip == "127.0.0.1"


def test_get_client_ip_returns_valid_ip(factory):
    request = factory.get("/")
    request.META["HTTP_X_FORWARDED_FOR"] = "192.0.2.123"
    ip = get_client_ip(request)

    # Validate that it's a valid IP (IPv4 or IPv6)
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        pytest.fail(f"{ip} is not a valid IP address")


@pytest.mark.parametrize(
    "header_ip",
    [
        "203.0.113.1",  # IPv4
        "2001:0db8:85a3::8a2e:370:7334",  # IPv6
    ],
)
def test_get_client_ip_valid_format(factory, header_ip):
    request = factory.get("/")
    request.META["HTTP_X_FORWARDED_FOR"] = header_ip
    ip = get_client_ip(request)

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        pytest.fail(f"{ip} is not a valid IP address")
