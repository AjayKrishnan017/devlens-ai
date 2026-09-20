from pprint import pprint

from app.services.label_engine import LabelEngine


engine = LabelEngine()


messages = [
    "fix docs ref",
    "fix typo in README",
    "Fix crash when session is missing",
    "Fix incorrect request handling",
    "Resolve regression in JSON parsing",
    "Update documentation",
    "Fix formatting",
    "Fix security vulnerability in cookie handling",
    "Add new feature",
    "Fix failing test for request context",
]


for message in messages:

    print("\n" + "=" * 70)

    print(
        "COMMIT:",
        message
    )

    result = engine.classify(
        message
    )

    pprint(result)