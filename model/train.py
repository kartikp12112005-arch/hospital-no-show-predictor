

import json
import os
import sys

import joblib
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.class_weight import compute_sample_weight

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from model.data_cleaning import clean_dataset, load_dataset  # noqa: E402
from model.evaluate import evaluate_model  # noqa: E402
from model.feature_engineering import (  # noqa: E402
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    engineer_features,
)
from model.visualize import (  # noqa: E402
    compute_dataset_stats,
    generate_eda_charts,
    save_dataset_stats,
)

DATASET_PATH = os.path.join(BASE_DIR, "dataset", "KaggleV2-May-2016.csv")
MODEL_OUTPUT_PATH = os.path.join(BASE_DIR, "trained_models", "best_model.pkl")
SCALER_OUTPUT_PATH = os.path.join(BASE_DIR, "trained_models", "scaler.pkl")
METRICS_OUTPUT_PATH = os.path.join(BASE_DIR, "trained_models", "metrics.json")


def build_candidate_models() -> dict:
    """Instantiate the four required candidate models with sane defaults."""
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=8, class_weight="balanced", random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150, max_depth=3, learning_rate=0.1, random_state=42
        ),
    }


def main():
    print("=" * 60)
    print("Smart Hospital No-Show Predictor — Model Training Pipeline")
    print("=" * 60)

    print("\n[1/6] Loading dataset...")
    raw_df = load_dataset(DATASET_PATH)
    print(f"      Loaded {len(raw_df):,} raw rows.")

    print("\n[2/6] Cleaning dataset...")
    clean_df = clean_dataset(raw_df)
    print(f"      {len(clean_df):,} rows remain after cleaning.")

    print("\n[3/6] Engineering features...")
    feature_df = engineer_features(clean_df)
    print(f"      Feature columns: {FEATURE_COLUMNS}")

    print("\n[4/6] Generating EDA charts + dataset stats...")
    generate_eda_charts(clean_df)
    stats = compute_dataset_stats(clean_df)
    save_dataset_stats(stats)

    print("\n[5/6] Splitting data and training candidate models...")
    X = feature_df[FEATURE_COLUMNS]
    y = feature_df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

  
    balanced_sample_weight = compute_sample_weight(class_weight="balanced", y=y_train)

    results = {}
    fitted_models = {}

    for name, model in build_candidate_models().items():
        print(f"      Training {name}...")
        if name == "Gradient Boosting":
            model.fit(X_train_scaled, y_train, sample_weight=balanced_sample_weight)
        else:
            model.fit(X_train_scaled, y_train)
        metrics = evaluate_model(model, X_test_scaled, y_test)
        results[name] = metrics
        fitted_models[name] = model
        print(f"        -> {metrics}")

    print("\n[6/6] Comparing models and saving the best one...")
  
    best_name = max(results, key=lambda n: results[n]["f1_score"])
    best_model = fitted_models[best_name]
    print(
        f"      Best model: {best_name} "
        f"(F1 = {results[best_name]['f1_score']}, ROC-AUC = {results[best_name]['roc_auc']})"
    )

    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    joblib.dump(best_model, MODEL_OUTPUT_PATH)
    joblib.dump(scaler, SCALER_OUTPUT_PATH)

    metadata = {
        "best_model": best_name,
        "feature_columns": FEATURE_COLUMNS,
        "all_results": results,
        "trained_rows": len(feature_df),
        "test_rows": len(X_test),
    }
    with open(METRICS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved best model  -> {MODEL_OUTPUT_PATH}")
    print(f"Saved scaler      -> {SCALER_OUTPUT_PATH}")
    print(f"Saved metrics     -> {METRICS_OUTPUT_PATH}")
    print("\nTraining complete.")


if __name__ == "__main__":
    main()
