"""
Input validation module for the appointment prediction form.

Centralizes all validation logic so both the HTML form route and the
JSON API route (/api/predict) share identical, well-tested rules.
"""

ALLOWED_GENDERS = {"M", "F"}


class ValidationError(Exception):
    """Raised when submitted form/JSON data fails validation."""


def _to_int(value, field_name, min_val=None, max_val=None, required=True):
    """Convert a value to int with friendly bounds checking."""
    if value in (None, ""):
        if required:
            raise ValidationError(f"{field_name} is required.")
        return 0

    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a whole number.")

    if min_val is not None and value < min_val:
        raise ValidationError(f"{field_name} cannot be less than {min_val}.")
    if max_val is not None and value > max_val:
        raise ValidationError(f"{field_name} cannot be more than {max_val}.")

    return value


def validate_predict_form(form) -> dict:
    """
    Validate raw form/JSON input for a prediction request.

    Args:
        form: A dict-like object (request.form or parsed JSON body).

    Returns:
        A cleaned dict of typed values ready for the ML pipeline.

    Raises:
        ValidationError: if any field is missing, malformed, or out of range.
    """
    gender = str(form.get("gender", "")).strip().upper()
    if gender not in ALLOWED_GENDERS:
        raise ValidationError("Gender must be 'M' (Male) or 'F' (Female).")

    age = _to_int(form.get("age"), "Age", min_val=0, max_val=120)
    scholarship = _to_int(form.get("scholarship", 0), "Scholarship", 0, 1, required=False)
    hypertension = _to_int(form.get("hypertension", 0), "Hypertension", 0, 1, required=False)
    diabetes = _to_int(form.get("diabetes", 0), "Diabetes", 0, 1, required=False)
    alcoholism = _to_int(form.get("alcoholism", 0), "Alcoholism", 0, 1, required=False)
    handicap = _to_int(form.get("handicap", 0), "Handicap", 0, 4, required=False)
    sms_received = _to_int(form.get("sms_received", 0), "SMS Received", 0, 1, required=False)
    waiting_days = _to_int(form.get("waiting_days"), "Waiting Days", min_val=0, max_val=365)

    return {
        "gender": gender,
        "age": age,
        "scholarship": scholarship,
        "hypertension": hypertension,
        "diabetes": diabetes,
        "alcoholism": alcoholism,
        "handicap": handicap,
        "sms_received": sms_received,
        "waiting_days": waiting_days,
    }
