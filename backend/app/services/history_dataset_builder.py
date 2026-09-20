import csv
from pathlib import Path

from app.services.feature_extractor import FeatureExtractor
from app.services.git_analyzer import GitAnalyzer
from app.services.dataset_builder import FEATURE_NAMES
from app.services.label_engine import LabelEngine


class HistoryDatasetBuilder:
    """
    Builds ML-ready datasets from the Git history of
    real Python repositories.

    Positive label:
        bugfix_touched

    Control label:
        no_bugfix_observed

    IMPORTANT:
    no_bugfix_observed does NOT mean bug-free.
    It only means that the file was not observed in one
    of the accepted bug-fix commits in our scan.
    """

    def __init__(self, repository_path):

        self.repository_path = Path(
            repository_path
        ).resolve()

        self.git = GitAnalyzer(
            self.repository_path
        )

        self.label_engine = LabelEngine()

        self.rows = []

        self.stats = {
            "commits_scanned": 0,
            "keyword_bugfix_commits": 0,
            "accepted_bugfix_commits": 0,
            "rejected_low_confidence": 0,
            "python_files_found": 0,
            "bugfix_samples_created": 0,
            "control_samples_created": 0,
            "missing_pre_fix_files": 0,
            "analysis_failures": 0,
            "duplicates_skipped": 0,
        }

    # =========================================================
    # Feature extraction
    # =========================================================

    def extract_features(self, code):
        """
        Run the DevLens FeatureExtractor.
        """

        result = FeatureExtractor(
            code
        ).extract()

        if not result["success"]:

            self.stats[
                "analysis_failures"
            ] += 1

            return None

        return result["features"]

    # =========================================================
    # Positive sample creation
    # =========================================================

    def build_bugfix_sample(
        self,
        code,
        commit,
        file_path,
        label_result,
    ):
        """
        Build one bugfix_touched sample using
        the source code BEFORE the fix.
        """

        features = self.extract_features(
            code
        )

        if features is None:
            return None

        row = {
            name: features[name]
            for name in FEATURE_NAMES
        }

        try:

            commit_stats = (
                self.git.get_commit_stats(
                    commit["hash"]
                )
            )

        except RuntimeError:

            commit_stats = {
                "lines_added": 0,
                "lines_deleted": 0,
                "files_changed": 0,
            }

        row.update({

            "label":
                "bugfix_touched",

            "label_confidence":
                label_result[
                    "confidence"
                ],

            "label_score":
                label_result[
                    "score"
                ],

            "repository":
                self.repository_path.name,

            "file":
                file_path,

            "commit":
                commit["hash"],

            "commit_date":
                commit["date"],

            "commit_message":
                commit["message"],

            "version":
                "before_fix",

            "commit_lines_added":
                commit_stats[
                    "lines_added"
                ],

            "commit_lines_deleted":
                commit_stats[
                    "lines_deleted"
                ],

            "commit_files_changed":
                commit_stats[
                    "files_changed"
                ],
        })

        return row

    # =========================================================
    # Collect bug-fix samples
    # =========================================================

    def collect_bugfix_samples(
        self,
        commit_limit=500
    ):
        """
        Scan Git history and collect Python files
        immediately before likely bug-fix commits.
        """

        commits = self.git.get_commits(
            limit=commit_limit
        )

        self.stats[
            "commits_scanned"
        ] = len(commits)

        seen_samples = set()

        for commit in commits:

            # First-stage keyword detector
            if not commit["bug_fix"]:
                continue

            self.stats[
                "keyword_bugfix_commits"
            ] += 1

            # Second-stage confidence analysis
            label_result = (
                self.label_engine.classify(
                    commit["message"]
                )
            )

            if not label_result[
                "is_bugfix_candidate"
            ]:

                self.stats[
                    "rejected_low_confidence"
                ] += 1

                continue

            self.stats[
                "accepted_bugfix_commits"
            ] += 1

            try:

                python_files = (
                    self.git
                    .get_changed_python_files(
                        commit["hash"]
                    )
                )

            except RuntimeError:
                continue

            self.stats[
                "python_files_found"
            ] += len(
                python_files
            )

            for file_path in python_files:

                sample_key = (
                    commit["hash"],
                    file_path,
                )

                if sample_key in seen_samples:

                    self.stats[
                        "duplicates_skipped"
                    ] += 1

                    continue

                try:

                    code = (
                        self.git
                        .get_file_before_commit(
                            commit["hash"],
                            file_path,
                        )
                    )

                except RuntimeError:

                    code = None

                if not code:

                    self.stats[
                        "missing_pre_fix_files"
                    ] += 1

                    continue

                row = (
                    self.build_bugfix_sample(
                        code=code,
                        commit=commit,
                        file_path=file_path,
                        label_result=label_result,
                    )
                )

                if row is None:
                    continue

                self.rows.append(
                    row
                )

                seen_samples.add(
                    sample_key
                )

                self.stats[
                    "bugfix_samples_created"
                ] += 1

        return [
            row
            for row in self.rows
            if row["label"]
            == "bugfix_touched"
        ]

    # =========================================================
    # Control sample creation
    # =========================================================

    def build_control_sample(
        self,
        code,
        file_path
    ):
        """
        Build one no_bugfix_observed control sample.
        """

        features = self.extract_features(
            code
        )

        if features is None:
            return None

        row = {
            name: features[name]
            for name in FEATURE_NAMES
        }

        row.update({

            "label":
                "no_bugfix_observed",

            "label_confidence":
                "CONTROL",

            "label_score":
                0,

            "repository":
                self.repository_path.name,

            "file":
                file_path,

            "commit":
                "HEAD",

            "commit_date":
                "",

            "commit_message":
                "",

            "version":
                "current",

            "commit_lines_added":
                0,

            "commit_lines_deleted":
                0,

            "commit_files_changed":
                0,
        })

        return row

    # =========================================================
    # Collect control samples
    # =========================================================

    def collect_control_samples(
        self,
        max_samples=100
    ):
        """
        Collect current Python files that were not part
        of the accepted bug-fix samples.

        These are controls, not guaranteed bug-free files.
        """

        if max_samples <= 0:
            return 0

        bugfix_files = {
            row["file"]
            for row in self.rows
            if row["label"]
            == "bugfix_touched"
        }

        try:

            output = self.git.run_git(
                "ls-files",
                "*.py"
            )

        except RuntimeError:

            return 0

        python_files = sorted({
            path.strip()
            for path in output.splitlines()
            if path.strip()
        })

        control_count = 0

        existing_controls = {
            row["file"]
            for row in self.rows
            if row["label"]
            == "no_bugfix_observed"
        }

        for file_path in python_files:

            if control_count >= max_samples:
                break

            # Don't use known bug-fix files
            # as controls.
            if file_path in bugfix_files:
                continue

            # Avoid duplicate controls.
            if file_path in existing_controls:

                self.stats[
                    "duplicates_skipped"
                ] += 1

                continue

            full_path = (
                self.repository_path
                / file_path
            )

            if not full_path.exists():
                continue

            if not full_path.is_file():
                continue

            try:

                code = full_path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

            except OSError:
                continue

            if not code.strip():
                continue

            row = (
                self.build_control_sample(
                    code=code,
                    file_path=file_path
                )
            )

            if row is None:
                continue

            self.rows.append(
                row
            )

            existing_controls.add(
                file_path
            )

            control_count += 1

        self.stats[
            "control_samples_created"
        ] += control_count

        return control_count

    # =========================================================
    # Dataset statistics
    # =========================================================

    def get_label_counts(self):
        """
        Count samples belonging to each label.
        """

        counts = {}

        for row in self.rows:

            label = row["label"]

            counts[label] = (
                counts.get(
                    label,
                    0
                )
                + 1
            )

        return counts

    def get_stats(self):
        """
        Return dataset collection statistics.
        """

        result = self.stats.copy()

        result[
            "total_samples"
        ] = len(self.rows)

        result[
            "label_counts"
        ] = self.get_label_counts()

        return result

    # =========================================================
    # CSV export
    # =========================================================

    def save(
        self,
        output_path
    ):
        """
        Save the complete dataset as CSV.
        """

        if not self.rows:

            raise ValueError(
                "Dataset contains no samples."
            )

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        metadata_fields = [

            "label",

            "label_confidence",

            "label_score",

            "repository",

            "file",

            "commit",

            "commit_date",

            "commit_message",

            "version",

            "commit_lines_added",

            "commit_lines_deleted",

            "commit_files_changed",
        ]

        fieldnames = (
            FEATURE_NAMES
            + metadata_fields
        )

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            writer.writerows(
                self.rows
            )

        return output_path