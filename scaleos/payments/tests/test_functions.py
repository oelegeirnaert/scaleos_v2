import pytest

from scaleos.payments.functions import ReferenceGenerator


def test_generate_and_validate_structured_reference():
    for _ in range(10):
        ref = ReferenceGenerator.generate_structured_reference()
        assert ReferenceGenerator.validate_structured_reference(ref)
        assert len(ReferenceGenerator.to_plain(ref)) == 12


def test_generate_structured_with_base_number():
    ref = ReferenceGenerator.generate_structured_reference(base_number="1234567")
    plain = ReferenceGenerator.to_plain(ref)
    assert plain.startswith("0001234567")
    assert ReferenceGenerator.validate_structured_reference(ref)


def test_generate_decorated_structured_reference():
    ref = ReferenceGenerator.generate_structured_reference(decorated=True)
    assert ref.startswith("+++")
    assert ref.endswith("+++")
    assert ReferenceGenerator.validate_structured_reference(ref)


def test_structured_validation_failures():
    with pytest.raises(ValueError):  # noqa: PT011
        ReferenceGenerator.validate_structured_reference("+++111/1111/11111+++")

    with pytest.raises(ValueError):  # noqa: PT011
        ReferenceGenerator.validate_structured_reference("1234567")


def test_iso11649_generation():
    ref = ReferenceGenerator.generate_iso11649_reference("539007547034")
    assert ref.startswith("RF")
    assert len(ref) <= 25
    assert ref[2:4].isdigit()


def test_iso11649_too_long():
    with pytest.raises(ValueError):  # noqa: PT011
        ReferenceGenerator.generate_iso11649_reference("A" * 22)
