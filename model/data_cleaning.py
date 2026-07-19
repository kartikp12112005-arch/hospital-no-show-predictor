
import pandas as pd


def load_dataset(csv_path: str) -> pd.DataFrame:
    """Load the raw dataset from disk."""
    return pd.read_csv(csv_path)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    
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

    df = df[(df["Age"] >= 0) & (df["Age"] <= 115)]

    df = df.dropna(subset=["Gender", "Age", "NoShow", "ScheduledDay", "AppointmentDay"])

    removed = before - len(df)
    print(f"[data_cleaning] Removed {removed} invalid/duplicate rows out of {before}.")

    return df.reset_index(drop=True)
