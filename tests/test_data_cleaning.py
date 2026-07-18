"""Unit tests for model/data_cleaning.py."""

import pandas as pd

from model.data_cleaning import clean_dataset


def _make_raw_df(rows):
    """Build a minimal raw dataframe matching the real Kaggle column names."""
    return pd.DataFrame(rows)


def test_clean_dataset_renames_typo_columns():
    df = _make_raw_df([
        {
            "PatientId": 1, "AppointmentID": 100, "Gender": "F",
            "ScheduledDay": "2016-04-01T10:00:00Z", "AppointmentDay": "2016-04-05T00:00:00Z",
            "Age": 30, "Neighbourhood": "X", "Scholarship": 0, "Hipertension": 1,
            "Diabetes": 0, "Alcoholism": 0, "Handcap": 0, "SMS_received": 1, "No-show": "No",
        }
    ])
    cleaned = clean_dataset(df)
    assert "Hypertension" in cleaned.columns
    assert "Handicap" in cleaned.columns
    assert "NoShow" in cleaned.columns


def test_clean_dataset_removes_invalid_ages():
    df = _make_raw_df([
        {"PatientId": 1, "AppointmentID": 1, "Gender": "F", "ScheduledDay": "2016-04-01T10:00:00Z",
         "AppointmentDay": "2016-04-05T00:00:00Z", "Age": -1, "Neighbourhood": "X", "Scholarship": 0,
         "Hipertension": 0, "Diabetes": 0, "Alcoholism": 0, "Handcap": 0, "SMS_received": 0, "No-show": "No"},
        {"PatientId": 2, "AppointmentID": 2, "Gender": "M", "ScheduledDay": "2016-04-01T10:00:00Z",
         "AppointmentDay": "2016-04-05T00:00:00Z", "Age": 200, "Neighbourhood": "X", "Scholarship": 0,
         "Hipertension": 0, "Diabetes": 0, "Alcoholism": 0, "Handcap": 0, "SMS_received": 0, "No-show": "No"},
        {"PatientId": 3, "AppointmentID": 3, "Gender": "M", "ScheduledDay": "2016-04-01T10:00:00Z",
         "AppointmentDay": "2016-04-05T00:00:00Z", "Age": 45, "Neighbourhood": "X", "Scholarship": 0,
         "Hipertension": 0, "Diabetes": 0, "Alcoholism": 0, "Handcap": 0, "SMS_received": 0, "No-show": "No"},
    ])
    cleaned = clean_dataset(df)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["Age"] == 45


def test_clean_dataset_removes_duplicate_appointment_ids():
    row = {
        "PatientId": 1, "AppointmentID": 500, "Gender": "F", "ScheduledDay": "2016-04-01T10:00:00Z",
        "AppointmentDay": "2016-04-05T00:00:00Z", "Age": 30, "Neighbourhood": "X", "Scholarship": 0,
        "Hipertension": 0, "Diabetes": 0, "Alcoholism": 0, "Handcap": 0, "SMS_received": 0, "No-show": "No",
    }
    df = _make_raw_df([row, row])
    cleaned = clean_dataset(df)
    assert len(cleaned) == 1
