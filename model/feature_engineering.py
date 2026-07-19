

import pandas as pd

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
   
    df = df.copy()

    
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
