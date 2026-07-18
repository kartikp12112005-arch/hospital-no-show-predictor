"""
Tests for utils/predictor.py.

These tests require model/train.py to have already been run at least
once (trained_models/best_model.pkl must exist), since predictor.py
loads that artifact at import time. If it's missing, these tests are
skipped rather than failing the whole suite.
"""

import os

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "trained_models", "best_model.pkl")

pytestmark = pytest.mark.skipif(
    not os.path.exists(MODEL_PATH),
    reason="Trained model not found — run `python model/train.py` first.",
)


def test_predict_no_show_returns_expected_keys():
    from utils.predictor import predict_no_show

    form_data = {
        "gender": "F", "age": 30, "scholarship": 0, "hypertension": 0,
        "diabetes": 0, "alcoholism": 0, "handicap": 0, "sms_received": 1,
        "waiting_days": 7,
    }
    result = predict_no_show(form_data)

    assert result["prediction"] in {"Attend", "No-Show"}
    assert result["risk_level"] in {"Low Risk", "High Risk"}
    assert 0 <= result["confidence"] <= 100
    assert abs(result["probability_attend"] + result["probability_no_show"] - 100) < 0.1


def test_predict_no_show_is_deterministic():
    from utils.predictor import predict_no_show

    form_data = {
        "gender": "M", "age": 60, "scholarship": 0, "hypertension": 1,
        "diabetes": 0, "alcoholism": 0, "handicap": 0, "sms_received": 1,
        "waiting_days": 3,
    }
    result_1 = predict_no_show(form_data)
    result_2 = predict_no_show(form_data)
    assert result_1 == result_2


def test_high_risk_and_low_risk_are_distinguishable():
    """
    Sanity check: a patient with a long wait and no SMS reminder should
    not score identically to one with a short wait and an SMS reminder.
    This doesn't assert a specific direction (that's a model property,
    not a contract) but confirms the features actually influence output.
    """
    from utils.predictor import predict_no_show

    profile_a = {
        "gender": "F", "age": 25, "scholarship": 0, "hypertension": 0,
        "diabetes": 0, "alcoholism": 0, "handicap": 0, "sms_received": 0,
        "waiting_days": 60,
    }
    profile_b = {
        "gender": "F", "age": 25, "scholarship": 0, "hypertension": 0,
        "diabetes": 0, "alcoholism": 0, "handicap": 0, "sms_received": 1,
        "waiting_days": 0,
    }
    result_a = predict_no_show(profile_a)
    result_b = predict_no_show(profile_b)
    assert result_a["probability_no_show"] != result_b["probability_no_show"]


def test_get_model_metadata_reports_all_four_models():
    from utils.predictor import get_model_metadata

    metadata = get_model_metadata()
    assert "best_model" in metadata
    assert len(metadata["all_results"]) == 4
    for metrics in metadata["all_results"].values():
        for key in ("accuracy", "precision", "recall", "f1_score", "roc_auc"):
            assert key in metrics
