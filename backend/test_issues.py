from app.analyzers.issue_detector import IssueDetector


code = """
from math import *


def process_users(users=[]):

    # TODO: validate user input

    try:
        expression = input("Expression: ")

        result = eval(expression)

        return result

    except:
        pass
"""


detector = IssueDetector(code)

issues = detector.analyze()

print("DEVLENS AI")
print("-" * 40)

for issue in issues:
    print(
        f"[{issue['severity']}] "
        f"{issue['type']} "
        f"(line {issue['line']})"
    )

    print(issue["message"])
    print()