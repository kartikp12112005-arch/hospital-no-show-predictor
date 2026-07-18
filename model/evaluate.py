"""
Model evaluation module.

Computes the standard classification metrics used to compare
candidate models: Accuracy, Precision, Recall, F1 Score, and ROC-AUC.
"""

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_model(model, X_test, y_test) -> dict:
    """
    Evaluate a fitted classifier on held-out test data.

    Args:
        model: A fitted scikit-learn classifier with predict/predict_proba.
        X_test: Scaled test features.
        y_test: True test labels.

    Returns:
        Dict of rounded metric values.
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    return {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
    }
