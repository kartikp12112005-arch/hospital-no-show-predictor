"""
Feature engineering module.

Derives the exact feature set the web form collects from the raw
Kaggle columns, so training features and inference-time features are
always perfectly aligned. This is the single source of truth for
which fields the model expects, in which order.
"""

import pandas as pd

# Order matters: utils/predictor.py must build feature vectors in
# this exact order at inference time.
FEATURE_COLUMNS = [
    "gender",
    "age",
    "scholarship",
    "hypertension",
    "diabetes",
    "alcoholism",
    "handicap",
    "sms_received",
    "waiting_days",
]
TARGET_COLUMN = "no_show"


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the ML-ready feature dataframe from a cleaned raw dataframe.

    Args:
        df: Cleaned dataframe from model.data_cleaning.clean_dataset.

    Returns:
        A dataframe with FEATURE_COLUMNS + TARGET_COLUMN, ready for
        train/test split.
    """
    df = df.copy()

    # Waiting days = how long between booking and the actual appointment.
    # A handful of rows have negative values (data-entry errors); clip to 0.
    waiting_days = (df["AppointmentDay"] - df["ScheduledDay"]).dt.days
    waiting_days = waiting_days.clip(lower=0)

    gender_encoded = df["Gender"].map({"M": 1, "F": 0})

    features = pd.DataFrame(
        {
            "gender": gender_encoded,
            "age": df["Age"],
            "scholarship": df["Scholarship"],
            "hypertension": df["Hypertension"],
            "diabetes": df["Diabetes"],
            "alcoholism": df["Alcoholism"],
            "handicap": df["Handicap"].clip(upper=4),
            "sms_received": df["SMS_received"],
            "waiting_days": waiting_days,
        }
    )

    features[TARGET_COLUMN] = df["NoShow"].map({"Yes": 1, "No": 0})

    return features.dropna().reset_index(drop=True)
