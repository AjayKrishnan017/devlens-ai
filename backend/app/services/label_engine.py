import re


class LabelEngine:
    """
    Estimates how strongly a Git commit message suggests
    an actual software defect fix.

    This is heuristic labeling, not ground truth.
    """

    STRONG_SIGNALS = {
        "bug",
        "bugfix",
        "defect",
        "regression",
        "crash",
        "exception",
        "incorrect",
        "failure",
        "failed",
        "broken",
        "error",
        "fault",
    }

    FIX_SIGNALS = {
        "fix",
        "fixed",
        "fixes",
        "resolve",
        "resolved",
        "correct",
        "corrected",
        "repair",
        "repaired",
    }

    WEAK_CONTEXT = {
        "docs",
        "doc",
        "documentation",
        "typo",
        "spelling",
        "formatting",
        "format",
        "readme",
        "comment",
        "comments",
        "changelog",
        "style",
        "lint",
        "whitespace",
    }

    TEST_CONTEXT = {
        "test",
        "tests",
        "testing",
    }

    SECURITY_CONTEXT = {
        "security",
        "vulnerability",
        "cve",
        "injection",
        "xss",
        "csrf",
        "exploit",
    }

    def tokenize(self, message):
        return set(
            re.findall(
                r"[a-zA-Z]+",
                message.lower()
            )
        )

    def classify(self, message):
        words = self.tokenize(message)

        strong_matches = (
            words & self.STRONG_SIGNALS
        )

        fix_matches = (
            words & self.FIX_SIGNALS
        )

        weak_matches = (
            words & self.WEAK_CONTEXT
        )

        test_matches = (
            words & self.TEST_CONTEXT
        )

        security_matches = (
            words & self.SECURITY_CONTEXT
        )

        score = 0
        reasons = []

        # Strong defect terminology
        if strong_matches:
            score += 3

            reasons.append(
                "strong_defect_language"
            )

        # Generic fix terminology
        if fix_matches:
            score += 2

            reasons.append(
                "fix_language"
            )

        # Security-related fixes are important
        if security_matches:
            score += 3

            reasons.append(
                "security_context"
            )

        # Tests can provide additional evidence,
        # but should not alone establish a defect.
        if test_matches:
            score += 1

            reasons.append(
                "test_context"
            )

        # Documentation / typo / formatting fixes
        # are weak evidence of a software defect.
        if weak_matches:
            score -= 4

            reasons.append(
                "non_code_context"
            )

        score = max(
            0,
            min(score, 10)
        )

        if score >= 5:
            confidence = "HIGH"

        elif score >= 3:
            confidence = "MEDIUM"

        elif score >= 1:
            confidence = "LOW"

        else:
            confidence = "NONE"

        is_candidate = confidence in {
            "HIGH",
            "MEDIUM"
        }

        return {
            "message": message,
            "score": score,
            "confidence": confidence,
            "is_bugfix_candidate": is_candidate,
            "signals": {
                "strong": sorted(
                    strong_matches
                ),
                "fix": sorted(
                    fix_matches
                ),
                "weak": sorted(
                    weak_matches
                ),
                "test": sorted(
                    test_matches
                ),
                "security": sorted(
                    security_matches
                ),
            },
            "reasons": reasons,
        }