"""
Prediction module.

Loads the best trained model + its scaler from trained_models/ (produced
by model/train.py) and exposes predict_no_show(), the single function
app.py calls to turn validated form input into a prediction result.

Importing this module raises an exception if the model hasn't been
trained yet — app.py catches that and disables prediction routes
gracefully instead of crashing the whole site.
"""

import json
import os
import sys

import joblib
import pandas as pd

# Ensure the project root is importable so this module works whether
# Flask is launched from the project root or elsewhere.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from model.feature_engineering import FEATURE_COLUMNS as FEATURE_ORDER  # noqa: E402

MODEL_PATH = os.path.join(BASE_DIR, "trained_models", "best_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "trained_models", "scaler.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "trained_models", "metrics.json")

_model = joblib.load(MODEL_PATH)
_scaler = joblib.load(SCALER_PATH)

with open(METRICS_PATH, "r", encoding="utf-8") as _f:
    _metadata = json.load(_f)


def predict_no_show(form_data: dict) -> dict:
    """
    Run a prediction for a single patient.

    Args:
        form_data: Cleaned dict produced by utils.validators.validate_predict_form,
            containing gender, age, scholarship, hypertension, diabetes,
            alcoholism, handicap, sms_received, waiting_days.

    Returns:
        dict with keys: prediction ('Attend'/'No-Show'), confidence (%),
        risk_level ('Low Risk'/'High Risk'), probability_attend,
        probability_no_show.
    """
    gender_encoded = 1 if form_data["gender"] == "M" else 0

    raw_features = {
        "gender": gender_encoded,
        "age": form_data["age"],
        "scholarship": form_data["scholarship"],
        "hypertension": form_data["hypertension"],
        "diabetes": form_data["diabetes"],
        "alcoholism": form_data["alcoholism"],
        "handicap": form_data["handicap"],
        "sms_received": form_data["sms_received"],
        "waiting_days": form_data["waiting_days"],
    }

    X = pd.DataFrame([raw_features], columns=FEATURE_ORDER)
    X_scaled = _scaler.transform(X)

    proba_no_show = float(_model.predict_proba(X_scaled)[0][1])
    is_no_show = proba_no_show >= 0.5

    prediction = "No-Show" if is_no_show else "Attend"
    risk_level = "High Risk" if is_no_show else "Low Risk"
    confidence = round((proba_no_show if is_no_show else 1 - proba_no_show) * 100, 2)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "risk_level": risk_level,
        "probability_attend": round((1 - proba_no_show) * 100, 2),
        "probability_no_show": round(proba_no_show * 100, 2),
    }


def get_model_metadata() -> dict:
    """Return metadata about the currently loaded model (used by the
    Model Comparison page and About page)."""
    return {
        "model_type": type(_model).__name__,
        "feature_order": FEATURE_ORDER,
        **_metadata,
    }
