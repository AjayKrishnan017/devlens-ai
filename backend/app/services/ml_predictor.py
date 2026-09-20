import json
from pathlib import Path

import joblib
import pandas as pd

from app.services.feature_extractor import FeatureExtractor


class MLPredictor:

    def __init__(self):

        self.project_root = (
            Path(__file__)
            .resolve()
            .parents[3]
        )

        self.model_path = (
            self.project_root
            / "ml"
            / "models"
            / "devlens_model.pkl"
        )

        self.metadata_path = (
            self.project_root
            / "ml"
            / "models"
            / "model_metadata.json"
        )

        self.model = None
        self.metadata = None

        self.load_model()

    def load_model(self):

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"ML model not found: "
                f"{self.model_path}"
            )

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Model metadata not found: "
                f"{self.metadata_path}"
            )

        self.model = joblib.load(
            self.model_path
        )

        with self.metadata_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            self.metadata = json.load(
                file
            )

    def get_features(self, code):

        result = FeatureExtractor(
            code
        ).extract()

        if not result["success"]:
            return None

        return result["features"]

    def prepare_input(self, features):

        feature_names = (
            self.metadata["features"]
        )

        values = {
            feature: features.get(
                feature,
                0
            )
            for feature in feature_names
        }

        return pd.DataFrame(
            [values],
            columns=feature_names
        )

    def risk_level(self, probability):

        if probability >= 0.75:
            return "HIGH"

        if probability >= 0.45:
            return "MEDIUM"

        return "LOW"

    def predict(self, code):

        features = self.get_features(
            code
        )

        if features is None:

            return {
                "success": False,
                "message":
                    "Feature extraction failed."
            }

        model_input = self.prepare_input(
            features
        )

        prediction = int(
            self.model.predict(
                model_input
            )[0]
        )

        if hasattr(
            self.model,
            "predict_proba"
        ):

            probability = float(
                self.model.predict_proba(
                    model_input
                )[0][1]
            )

        else:

            probability = float(
                prediction
            )

        risk = self.risk_level(
            probability
        )

        return {
            "success": True,

            "prediction": prediction,

            "risk": risk,

            "probability": round(
                probability,
                4
            ),

            "probability_percent": round(
                probability * 100,
                2
            ),

            "model": self.metadata.get(
                "model_name"
            ),

            "model_version":
                self.metadata.get(
                    "model_version"
                ),

            "features": features,

            "disclaimer": (
                "Experimental defect-risk "
                "estimate based on historical "
                "repository patterns."
            ),
        }