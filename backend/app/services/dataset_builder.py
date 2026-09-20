import csv
from pathlib import Path

from app.services.feature_extractor import FeatureExtractor


FEATURE_NAMES = [
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


class DatasetBuilder:

    def __init__(self):
        self.rows = []

    def add_sample(self, code, label, source="unknown"):
        result = FeatureExtractor(code).extract()

        if not result["success"]:
            return False

        features = result["features"]

        row = {
            name: features[name]
            for name in FEATURE_NAMES
        }

        row["label"] = label
        row["source"] = source

        self.rows.append(row)

        return True

    def save(self, output_path):
        if not self.rows:
            raise ValueError("Dataset contains no samples.")

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = FEATURE_NAMES + [
            "label",
            "source"
        ]

        with path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(self.rows)

        return path