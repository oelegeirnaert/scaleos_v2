from scaleos.shared.functions import birthday_cleaning
from scaleos.shared.functions import mobile_phone_number_cleaning


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
