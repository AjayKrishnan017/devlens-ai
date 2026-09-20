from app.analyzers.syntax_analyzer import CodeAnalyzer
from app.analyzers.issue_detector import IssueDetector
from app.analyzers.complexity_analyzer import ComplexityAnalyzer


class FeatureExtractor:

    def __init__(self, code):
        self.code = code

    def extract(self):

        structure = CodeAnalyzer(
            self.code
        ).analyze_structure()

        issues = IssueDetector(
            self.code
        ).analyze()

        complexity_report = ComplexityAnalyzer(
            self.code
        ).analyze()

        if not structure.get("valid"):
            return {
                "success": False,
                "error": "Invalid Python code"
            }

        functions = complexity_report.get(
            "functions",
            []
        )

        if functions:
            complexities = [
                f["complexity"]
                for f in functions
            ]

            nestings = [
                f["nesting_depth"]
                for f in functions
            ]

            lengths = [
                f["length"]
                for f in functions
            ]

            parameters = [
                f["parameters"]
                for f in functions
            ]

            max_complexity = max(complexities)
            avg_complexity = sum(complexities) / len(complexities)

            max_nesting = max(nestings)
            avg_nesting = sum(nestings) / len(nestings)

            max_function_length = max(lengths)
            avg_function_length = sum(lengths) / len(lengths)

            max_parameters = max(parameters)

        else:
            max_complexity = 0
            avg_complexity = 0

            max_nesting = 0
            avg_nesting = 0

            max_function_length = 0
            avg_function_length = 0

            max_parameters = 0

        severity_counts = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0
        }

        for issue in issues:
            severity = issue.get("severity")

            if severity in severity_counts:
                severity_counts[severity] += 1

        metrics = structure["metrics"]

        features = {
            "function_count": metrics["function_count"],
            "class_count": metrics["class_count"],
            "loop_count": metrics["loop_count"],
            "conditional_count": metrics["conditional_count"],
            "try_block_count": metrics["try_block_count"],

            "max_complexity": max_complexity,
            "avg_complexity": round(avg_complexity, 2),

            "max_nesting": max_nesting,
            "avg_nesting": round(avg_nesting, 2),

            "max_function_length": max_function_length,
            "avg_function_length": round(
                avg_function_length,
                2
            ),

            "max_parameters": max_parameters,

            "total_issues": len(issues),

            "low_issues": severity_counts["LOW"],
            "medium_issues": severity_counts["MEDIUM"],
            "high_issues": severity_counts["HIGH"],
            "critical_issues": severity_counts["CRITICAL"]
        }

        return {
            "success": True,
            "features": features
        }