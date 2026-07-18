"""
Data cleaning module.

Loads the raw Kaggle "Medical Appointment No Shows" CSV and applies
cleaning rules: column standardization, date parsing, invalid-value
removal, and duplicate handling.
"""

import pandas as pd


def load_dataset(csv_path: str) -> pd.DataFrame:
    """Load the raw dataset from disk."""
    return pd.read_csv(csv_path)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw dataframe.

    Steps:
    - Strip/standardize column names (the original Kaggle file has typos:
      'Hipertension', 'Handcap', 'No-show')
    - Parse ScheduledDay / AppointmentDay as datetimes
    - Drop duplicate AppointmentID rows
    - Remove rows with invalid Age (negative or unrealistically high)
    - Drop rows with missing critical values

    Args:
        df: Raw dataframe as loaded from the CSV.

    Returns:
        A cleaned copy of the dataframe.
    """
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    df.rename(
        columns={
            "Hipertension": "Hypertension",
            "Handcap": "Handicap",
            "No-show": "NoShow",
        },
        inplace=True,
    )

    df["ScheduledDay"] = pd.to_datetime(df["ScheduledDay"])
    df["AppointmentDay"] = pd.to_datetime(df["AppointmentDay"])

    before = len(df)
    df = df.drop_duplicates(subset="AppointmentID")

    # The public dataset is known to contain a few rows with Age == -1
    # and a handful of unrealistic outliers; both are removed.
    df = df[(df["Age"] >= 0) & (df["Age"] <= 115)]

    df = df.dropna(subset=["Gender", "Age", "NoShow", "ScheduledDay", "AppointmentDay"])

    removed = before - len(df)
    print(f"[data_cleaning] Removed {removed} invalid/duplicate rows out of {before}.")

    return df.reset_index(drop=True)
