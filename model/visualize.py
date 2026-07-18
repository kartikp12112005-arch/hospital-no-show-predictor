"""
Visualization & EDA module.

Produces two kinds of output:
1. Static PNG charts saved to static/images/eda/ — useful for the
   notebooks/ EDA writeup and README screenshots.
2. dataset_stats.json — precomputed aggregates (gender/age/disease
   distribution, attendance rate, SMS effect, monthly trend) that the
   Analytics page reads directly instead of recomputing from the raw
   110k-row CSV on every request.
"""

import json
import os

import matplotlib

matplotlib.use("Agg")  # headless rendering, no display needed
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDA_IMAGE_DIR = os.path.join(BASE_DIR, "static", "images", "eda")
STATS_OUTPUT_PATH = os.path.join(BASE_DIR, "trained_models", "dataset_stats.json")


def generate_eda_charts(clean_df: pd.DataFrame) -> None:
    """Save a handful of exploratory matplotlib charts as PNG files."""
    os.makedirs(EDA_IMAGE_DIR, exist_ok=True)

    plt.figure(figsize=(5, 4))
    clean_df["Gender"].value_counts().plot(kind="bar", color=["#2f6fb3", "#f28fb1"])
    plt.title("Gender Distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_IMAGE_DIR, "gender_distribution.png"))
    plt.close()

    plt.figure(figsize=(6, 4))
    clean_df["Age"].plot(kind="hist", bins=30, color="#2f6fb3")
    plt.title("Age Distribution")
    plt.xlabel("Age")
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_IMAGE_DIR, "age_distribution.png"))
    plt.close()

    plt.figure(figsize=(5, 4))
    clean_df["NoShow"].value_counts().plot(kind="bar", color=["#2ecc71", "#e74c3c"])
    plt.title("Attendance vs No-Show")
    plt.tight_layout()
    plt.savefig(os.path.join(EDA_IMAGE_DIR, "attendance_distribution.png"))
    plt.close()

    print(f"[visualize] EDA charts saved to {EDA_IMAGE_DIR}")


def compute_dataset_stats(clean_df: pd.DataFrame) -> dict:
    """
    Precompute all the aggregates the Analytics page's Chart.js charts need.
    """
    df = clean_df.copy()
    df["waiting_days"] = (df["AppointmentDay"] - df["ScheduledDay"]).dt.days.clip(lower=0)
    # Drop timezone info before converting to a monthly period to avoid
    # silently losing precision warnings from pandas.
    df["month"] = df["AppointmentDay"].dt.tz_localize(None).dt.to_period("M").astype(str)

    def attendance_rate_by(column: str) -> dict:
        grouped = df.groupby(column)["NoShow"].apply(lambda s: round((s == "No").mean() * 100, 2))
        return {str(key): value for key, value in grouped.items()}

    age_bins = [0, 12, 18, 30, 45, 60, 120]
    age_labels = ["0-12", "13-18", "19-30", "31-45", "46-60", "60+"]
    df["age_group"] = pd.cut(df["Age"], bins=age_bins, labels=age_labels, right=True)

    stats = {
        "gender_distribution": {
            str(k): int(v) for k, v in df["Gender"].value_counts().to_dict().items()
        },
        "age_distribution": {
            str(k): int(v) for k, v in df["age_group"].value_counts().sort_index().to_dict().items()
        },
        "disease_distribution": {
            "Hypertension": int(df["Hypertension"].sum()),
            "Diabetes": int(df["Diabetes"].sum()),
            "Alcoholism": int(df["Alcoholism"].sum()),
            "Handicap": int((df["Handicap"] > 0).sum()),
        },
        "attendance_rate_overall": round((df["NoShow"] == "No").mean() * 100, 2),
        "sms_effect": attendance_rate_by("SMS_received"),
        "monthly_trend": {
            str(k): v
            for k, v in df.groupby("month")["NoShow"]
            .apply(lambda s: round((s == "No").mean() * 100, 2))
            .to_dict()
            .items()
        },
        "total_records": int(len(df)),
    }

    return stats


def save_dataset_stats(stats: dict) -> None:
    """Persist computed stats as JSON for fast reads by the Flask app."""
    os.makedirs(os.path.dirname(STATS_OUTPUT_PATH), exist_ok=True)
    with open(STATS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"[visualize] Dataset stats saved to {STATS_OUTPUT_PATH}")
