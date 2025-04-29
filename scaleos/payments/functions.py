import random
import string

from django.utils.translation import gettext_lazy as _


class ReferenceGenerator:
    @staticmethod
    def generate_structured_reference(base_number=None, *, decorated=False):
        """
        Generate a Belgian structured payment reference.
        """
        if base_number is None:
            base_number = str(random.randint(1_000_000, 9_999_999_999))  # noqa: S311
        else:
            base_number = "".join(filter(str.isdigit, str(base_number)))
            max_number = 10
            if len(base_number) > max_number:
                msg = _("base number must be max 10 digits.")
                raise ValueError(msg)

        base_number = base_number.zfill(10)

        checksum = 97 - (int(base_number) % 97)
        if checksum == 0:
            checksum = 97

        full_reference = f"{base_number}{checksum:02}"
        formatted = f"{full_reference[:3]}/{full_reference[3:7]}/{full_reference[7:]}"

        if decorated:
            return f"+++{formatted}+++"
        return formatted

    @staticmethod
    def validate_structured_reference(reference):
        """
        Validate a Belgian structured reference.
        """
        clean_reference = "".join(filter(str.isdigit, reference))
        exact_length = 12
        if len(clean_reference) != exact_length:
            msg = _("reference must be exactly 12 digits long.")
            raise ValueError(msg)

        base_number = clean_reference[:-2]
        checksum = int(clean_reference[-2:])

        calculated_checksum = 97 - (int(base_number) % 97)
        if calculated_checksum == 0:
            calculated_checksum = 97

        if checksum != calculated_checksum:
            calc_chksum = f"{calculated_checksum:02}"
            the_chksum = f"{checksum:02}"
            msg = _("Invalid checksum: expected %s, got %s") % (calc_chksum, the_chksum)
            raise ValueError(msg)

        return True

    @staticmethod
    def to_plain(reference):
        """
        Remove formatting (slashes, +++) from reference.
        """
        return "".join(filter(str.isalnum, reference))

    @staticmethod
    def generate_iso11649_reference(base_number):
        """
        Generate an ISO 11649 creditor reference.
        """
        base_number = "".join(filter(str.isalnum, str(base_number))).upper()
        max_len = 21
        if len(base_number) > max_len:
            msg = _("base reference too long for ISO 11649 format (max 21 characters).")
            raise ValueError(msg)

        temp = base_number + "RF00"
        translation = {
            char: str(10 + idx) for idx, char in enumerate(string.ascii_uppercase)
        }
        temp_numeric = "".join(translation.get(c, c) for c in temp)

        mod = int(temp_numeric) % 97
        checksum = 98 - mod
        checksum_str = f"{checksum:02}"

        return f"RF{checksum_str}{base_number}"
