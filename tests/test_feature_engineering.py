"""Unit tests for model/feature_engineering.py."""

import pandas as pd

from model.data_cleaning import clean_dataset
from model.feature_engineering import FEATURE_COLUMNS, TARGET_COLUMN, engineer_features


def _cleaned_sample():
    df = pd.DataFrame([
        {"PatientId": 1, "AppointmentID": 1, "Gender": "F", "ScheduledDay": "2016-04-01T10:00:00Z",
         "AppointmentDay": "2016-04-10T00:00:00Z", "Age": 30, "Neighbourhood": "X", "Scholarship": 0,
         "Hipertension": 1, "Diabetes": 0, "Alcoholism": 0, "Handcap": 0, "SMS_received": 1, "No-show": "No"},
        {"PatientId": 2, "AppointmentID": 2, "Gender": "M", "ScheduledDay": "2016-04-02T10:00:00Z",
         "AppointmentDay": "2016-04-02T00:00:00Z", "Age": 50, "Neighbourhood": "X", "Scholarship": 1,
         "Hipertension": 0, "Diabetes": 1, "Alcoholism": 0, "Handcap": 2, "SMS_received": 0, "No-show": "Yes"},
    ])
    return clean_dataset(df)


def test_engineered_features_have_expected_columns():
    features = engineer_features(_cleaned_sample())
    for col in FEATURE_COLUMNS:
        assert col in features.columns
    assert TARGET_COLUMN in features.columns


def test_gender_is_encoded_numerically():
    features = engineer_features(_cleaned_sample())
    assert set(features["gender"].unique()).issubset({0, 1})


def test_target_maps_yes_no_to_1_0():
    features = engineer_features(_cleaned_sample())
    # Row 1: No-show = 'No' -> 0 ; Row 2: No-show = 'Yes' -> 1
    assert 0 in features[TARGET_COLUMN].values
    assert 1 in features[TARGET_COLUMN].values


def test_waiting_days_is_non_negative():
    features = engineer_features(_cleaned_sample())
    assert (features["waiting_days"] >= 0).all()


def test_handicap_is_clipped_to_max_four():
    df = pd.DataFrame([
        {"PatientId": 1, "AppointmentID": 1, "Gender": "F", "ScheduledDay": "2016-04-01T10:00:00Z",
         "AppointmentDay": "2016-04-10T00:00:00Z", "Age": 30, "Neighbourhood": "X", "Scholarship": 0,
         "Hipertension": 0, "Diabetes": 0, "Alcoholism": 0, "Handcap": 9, "SMS_received": 0, "No-show": "No"},
    ])
    features = engineer_features(clean_dataset(df))
    assert features.iloc[0]["handicap"] <= 4
