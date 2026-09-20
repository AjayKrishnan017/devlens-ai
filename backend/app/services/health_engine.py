from app.analyzers.syntax_analyzer import CodeAnalyzer
from app.analyzers.issue_detector import IssueDetector
from app.analyzers.complexity_analyzer import ComplexityAnalyzer
from app.services.ml_predictor import MLPredictor


class HealthEngine:
    """
    Main DevLens analysis engine.

    Combines:
    - syntax / structure analysis
    - issue detection
    - complexity analysis
    - health scoring
    - security scoring
    - ML defect-risk prediction
    """

    SEVERITY_PENALTIES = {
        "LOW": 3,
        "MEDIUM": 8,
        "HIGH": 15,
        "CRITICAL": 25,
    }

    SECURITY_ISSUES = {
        "DANGEROUS_EVAL",
        "DANGEROUS_EXEC",
    }

    def __init__(self, code):
        self.code = code

        self.syntax_analyzer = CodeAnalyzer(
            code
        )

        self.issue_detector = IssueDetector(
            code
        )

        self.complexity_analyzer = ComplexityAnalyzer(
            code
        )

    # =========================================================
    # Health score
    # =========================================================

    def calculate_score(
        self,
        issues,
        complexity_report
    ):
        score = 100

        # -----------------------------------------------------
        # Issue penalties
        # -----------------------------------------------------

        for issue in issues:

            if not isinstance(issue, dict):
                continue

            severity = issue.get(
                "severity",
                "LOW"
            )

            penalty = (
                self.SEVERITY_PENALTIES.get(
                    severity,
                    0
                )
            )

            score -= penalty

        # -----------------------------------------------------
        # Complexity penalties
        # -----------------------------------------------------

        functions = complexity_report.get(
            "functions",
            []
        )

        if not isinstance(functions, list):
            functions = []

        for function in functions:

            if not isinstance(function, dict):
                continue

            complexity = function.get(
                "complexity",
                0
            )

            nesting = function.get(
                "nesting_depth",
                0
            )

            parameters = function.get(
                "parameters",
                0
            )

            length = function.get(
                "length",
                0
            )

            # Cyclomatic complexity
            if complexity > 20:
                score -= 20

            elif complexity > 10:
                score -= 10

            elif complexity > 5:
                score -= 3

            # Deep nesting
            if nesting > 4:
                score -= 5

            # Too many parameters
            if parameters > 5:
                score -= 3

            # Large function
            if length > 50:
                score -= 5

        return max(
            0,
            min(score, 100)
        )

    # =========================================================
    # Security score
    # =========================================================

    def calculate_security_score(
        self,
        issues
    ):
        score = 100

        for issue in issues:

            if not isinstance(issue, dict):
                continue

            issue_type = issue.get(
                "type"
            )

            if issue_type not in self.SECURITY_ISSUES:
                continue

            severity = issue.get(
                "severity",
                "LOW"
            )

            penalty = (
                self.SEVERITY_PENALTIES.get(
                    severity,
                    0
                )
            )

            score -= penalty

        return max(
            0,
            min(score, 100)
        )

    # =========================================================
    # Severity summary
    # =========================================================

    def count_severities(
        self,
        issues
    ):
        counts = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0,
        }

        for issue in issues:

            if not isinstance(issue, dict):
                continue

            severity = issue.get(
                "severity",
                "LOW"
            )

            if severity in counts:
                counts[severity] += 1

        return counts

    # =========================================================
    # Grade generation
    # =========================================================

    def generate_grade(
        self,
        score
    ):
        if score >= 90:
            return "A"

        if score >= 80:
            return "B"

        if score >= 70:
            return "C"

        if score >= 60:
            return "D"

        return "F"

    # =========================================================
    # Issue detector normalization
    # =========================================================

    def get_issues(self):
        """
        Normalize IssueDetector output.

        Some versions of IssueDetector return:

            [issue, issue, ...]

        while others may return:

            {
                "success": True,
                "issues": [...]
            }

        This method supports both.
        """

        try:

            result = (
                self.issue_detector
                .analyze()
            )

        except Exception:
            return []

        if isinstance(result, list):
            return result

        if isinstance(result, dict):

            issues = result.get(
                "issues",
                []
            )

            if isinstance(issues, list):
                return issues

        return []

    # =========================================================
    # Complexity normalization
    # =========================================================

    def get_complexity(self):
        """
        Safely obtain complexity analysis.
        """

        try:

            result = (
                self.complexity_analyzer
                .analyze()
            )

        except Exception as error:

            return {
                "success": False,
                "function_count": 0,
                "functions": [],
                "message": str(error),
            }

        if not isinstance(result, dict):

            return {
                "success": False,
                "function_count": 0,
                "functions": [],
                "message":
                    "Invalid complexity analyzer output.",
            }

        if "functions" not in result:
            result["functions"] = []

        if not isinstance(
            result["functions"],
            list
        ):
            result["functions"] = []

        return result

    # =========================================================
    # ML prediction
    # =========================================================

    def get_ml_prediction(self):
        """
        Run the trained DevLens ML model.

        ML errors should NOT cause the entire static
        analysis API to fail.
        """

        try:

            predictor = MLPredictor()

            result = predictor.predict(
                self.code
            )

            if not isinstance(result, dict):

                return {
                    "success": False,
                    "message":
                        "Invalid ML predictor output.",
                }

            return result

        except Exception as error:

            return {
                "success": False,
                "message": str(error),
            }

    # =========================================================
    # Main analysis
    # =========================================================

    def analyze(self):
        """
        Execute the complete DevLens analysis pipeline.
        """

        # -----------------------------------------------------
        # Syntax + structure
        # -----------------------------------------------------

        try:

            structure = (
                self.syntax_analyzer
                .analyze_structure()
            )

        except Exception as error:

            return {
                "success": False,
                "message":
                    f"Structure analysis failed: {error}",
            }

        if not isinstance(
            structure,
            dict
        ):

            return {
                "success": False,
                "message":
                    "Invalid structure analyzer output.",
            }

        if not structure.get(
            "valid",
            False
        ):

            return {
                "success": False,
                "message": structure.get(
                    "message",
                    "Invalid Python code."
                ),
            }

        # -----------------------------------------------------
        # Issues
        # -----------------------------------------------------

        issues = self.get_issues()

        # -----------------------------------------------------
        # Complexity
        # -----------------------------------------------------

        complexity = (
            self.get_complexity()
        )

        # -----------------------------------------------------
        # Scores
        # -----------------------------------------------------

        health_score = (
            self.calculate_score(
                issues,
                complexity
            )
        )

        security_score = (
            self.calculate_security_score(
                issues
            )
        )

        severity_summary = (
            self.count_severities(
                issues
            )
        )

        grade = self.generate_grade(
            health_score
        )

        # -----------------------------------------------------
        # ML
        # -----------------------------------------------------

        ml_prediction = (
            self.get_ml_prediction()
        )

        # -----------------------------------------------------
        # Final report
        # -----------------------------------------------------

        return {
            "success": True,

            "summary": {
                "health_score":
                    health_score,

                "grade":
                    grade,

                "security_score":
                    security_score,

                "total_issues":
                    len(issues),
            },

            "severity_summary":
                severity_summary,

            "structure":
                structure,

            "complexity":
                complexity,

            "issues":
                issues,

            "ml_prediction":
                ml_prediction,
        }