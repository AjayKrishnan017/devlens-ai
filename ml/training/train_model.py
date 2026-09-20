from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "flask_training_dataset.csv"
)

MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = (
    MODEL_DIR
    / "devlens_model.pkl"
)

METADATA_PATH = (
    MODEL_DIR
    / "model_metadata.json"
)


FEATURES = [
    "function_count",
    "class_count",
    "loop_count",
    "conditional_count",
    "try_block_count",
    "max_complexity",
    "avg_complexity",
    "max_nesting",
    "avg_nesting",
    "max_function_length",
    "avg_function_length",
    "max_parameters",
    "total_issues",
    "low_issues",
    "medium_issues",
    "high_issues",
    "critical_issues",
]


def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    required = set(FEATURES + ["label"])

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Dataset is missing columns: {missing}"
        )

    df = df.dropna(
        subset=FEATURES + ["label"]
    ).copy()

    df["target"] = (
        df["label"]
        == "bugfix_touched"
    ).astype(int)

    return df


def evaluate_model(
    name,
    model,
    X_test,
    y_test
):
    predictions = model.predict(
        X_test
    )

    if hasattr(
        model,
        "predict_proba"
    ):
        probabilities = (
            model.predict_proba(
                X_test
            )[:, 1]
        )
    else:
        probabilities = None

    metrics = {
        "accuracy": float(
            accuracy_score(
                y_test,
                predictions
            )
        ),

        "precision": float(
            precision_score(
                y_test,
                predictions,
                zero_division=0
            )
        ),

        "recall": float(
            recall_score(
                y_test,
                predictions,
                zero_division=0
            )
        ),

        "f1": float(
            f1_score(
                y_test,
                predictions,
                zero_division=0
            )
        ),
    }

    if (
        probabilities is not None
        and len(set(y_test)) > 1
    ):
        metrics["roc_auc"] = float(
            roc_auc_score(
                y_test,
                probabilities
            )
        )
    else:
        metrics["roc_auc"] = None

    print(
        f"\n=== {name} ===\n"
    )

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    print(
        "Confusion Matrix:"
    )

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    print(
        "\nMetrics:"
    )

    for key, value in metrics.items():
        print(
            f"{key}: {value}"
        )

    return metrics


def main():
    print(
        "\n=== DEVLENS ML TRAINING ===\n"
    )

    df = load_dataset()

    print(
        f"Dataset samples: {len(df)}"
    )

    print(
        "\nClass distribution:"
    )

    print(
        df["label"].value_counts()
    )

    if df["target"].nunique() < 2:
        raise ValueError(
            "Training requires both positive "
            "and control samples."
        )

    X = df[FEATURES]
    y = df["target"]

    class_counts = (
        y.value_counts()
    )

    if class_counts.min() < 2:
        raise ValueError(
            "Not enough samples in one of the "
            "classes for train/test splitting."
        )

    stratify = (
        y
        if class_counts.min() >= 2
        else None
    )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=42,
            stratify=stratify,
        )
    )

    print(
        f"\nTraining samples: "
        f"{len(X_train)}"
    )

    print(
        f"Testing samples: "
        f"{len(X_test)}"
    )

    logistic_model = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            )
        ),
    ])

    random_forest_model = (
        RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
    )

    print(
        "\nTraining Logistic Regression..."
    )

    logistic_model.fit(
        X_train,
        y_train
    )

    logistic_metrics = (
        evaluate_model(
            "Logistic Regression",
            logistic_model,
            X_test,
            y_test
        )
    )

    print(
        "\nTraining Random Forest..."
    )

    random_forest_model.fit(
        X_train,
        y_train
    )

    forest_metrics = (
        evaluate_model(
            "Random Forest",
            random_forest_model,
            X_test,
            y_test
        )
    )

    # F1 is used only as a simple baseline
    # selection rule for DevLens v1.
    if (
        forest_metrics["f1"]
        >= logistic_metrics["f1"]
    ):
        selected_name = (
            "RandomForestClassifier"
        )

        selected_model = (
            random_forest_model
        )

        selected_metrics = (
            forest_metrics
        )

    else:
        selected_name = (
            "LogisticRegression"
        )

        selected_model = (
            logistic_model
        )

        selected_metrics = (
            logistic_metrics
        )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        selected_model,
        MODEL_PATH
    )

    metadata = {
        "model_name": selected_name,
        "model_version": "devlens-v1",
        "features": FEATURES,
        "positive_class": "bugfix_touched",
        "negative_class":
            "no_bugfix_observed",
        "training_samples":
            int(len(X_train)),
        "test_samples":
            int(len(X_test)),
        "metrics":
            selected_metrics,
        "dataset":
            DATASET_PATH.name,
        "warning": (
            "Experimental baseline trained "
            "using heuristic historical labels."
        ),
    }

    with METADATA_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    print(
        "\n=== SELECTED MODEL ==="
    )

    print(
        selected_name
    )

    print(
        "\nModel saved:"
    )

    print(
        MODEL_PATH
    )

    print(
        "\nMetadata saved:"
    )

    print(
        METADATA_PATH
    )


if __name__ == "__main__":
    main()