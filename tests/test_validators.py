"""Unit tests for utils/validators.py."""

import pytest

from utils.validators import ValidationError, validate_predict_form


def test_valid_form_passes():
    form = {
        "gender": "f", "age": "45", "scholarship": "1", "hypertension": "0",
        "diabetes": "0", "alcoholism": "0", "handicap": "0",
        "sms_received": "1", "waiting_days": "10",
    }
    result = validate_predict_form(form)
    assert result["gender"] == "F"  # normalized to uppercase
    assert result["age"] == 45
    assert result["waiting_days"] == 10


def test_missing_age_raises():
    form = {"gender": "F", "waiting_days": "5"}
    with pytest.raises(ValidationError, match="Age is required"):
        validate_predict_form(form)


def test_invalid_gender_raises():
    form = {"gender": "X", "age": "30", "waiting_days": "5"}
    with pytest.raises(ValidationError, match="Gender must be"):
        validate_predict_form(form)


def test_non_numeric_age_raises():
    form = {"gender": "F", "age": "not-a-number", "waiting_days": "5"}
    with pytest.raises(ValidationError, match="whole number"):
        validate_predict_form(form)


@pytest.mark.parametrize("age", [-1, 200])
def test_age_out_of_bounds_raises(age):
    form = {"gender": "F", "age": str(age), "waiting_days": "5"}
    with pytest.raises(ValidationError):
        validate_predict_form(form)


def test_optional_fields_default_to_zero():
    form = {"gender": "M", "age": "50", "waiting_days": "0"}
    result = validate_predict_form(form)
    assert result["scholarship"] == 0
    assert result["hypertension"] == 0
    assert result["sms_received"] == 0


def test_handicap_out_of_bounds_raises():
    form = {"gender": "F", "age": "40", "waiting_days": "3", "handicap": "9"}
    with pytest.raises(ValidationError):
        validate_predict_form(form)
