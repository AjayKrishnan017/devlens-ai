from pprint import pprint

from app.services.history_dataset_builder import (
    HistoryDatasetBuilder
)


REPOSITORY = "../repositories/flask"

OUTPUT = (
    "../ml/data/"
    "flask_training_dataset.csv"
)


print("\n=== DEVLENS DATASET BUILDER ===\n")


builder = HistoryDatasetBuilder(
    REPOSITORY
)


print(
    "Collecting bug-fix samples..."
)

bugfix_samples = (
    builder.collect_bugfix_samples(
        commit_limit=500
    )
)

bugfix_count = len(
    bugfix_samples
)

print(
    f"Bug-fix samples: {bugfix_count}"
)


print(
    "\nCollecting control samples..."
)

control_count = (
    builder.collect_control_samples(
        max_samples=bugfix_count
    )
)

print(
    f"Control samples: {control_count}"
)


print(
    f"\nTotal samples: {len(builder.rows)}"
)


if builder.rows:

    path = builder.save(
        OUTPUT
    )

    print(
        f"Dataset saved: {path}"
    )


print(
    "\n=== DATASET STATISTICS ===\n"
)

pprint(
    builder.get_stats()
)