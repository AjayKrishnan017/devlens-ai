from pprint import pprint

from app.services.git_analyzer import GitAnalyzer


analyzer = GitAnalyzer(
    "../repositories/flask"
)


print("\n=== REPOSITORY SUMMARY ===\n")

summary = analyzer.get_repository_summary(
    commit_limit=100
)

pprint(summary)


print("\n=== BUG FIX COMMITS ===\n")

bug_fixes = analyzer.get_bug_fix_commits(
    limit=100
)

print(
    f"Potential bug fixes: {len(bug_fixes)}"
)


if bug_fixes:

    commit = bug_fixes[0]

    print("\nSelected commit:")
    pprint(commit)

    files = analyzer.get_changed_python_files(
        commit["hash"]
    )

    print("\nPython files changed:")

    for file_path in files:
        print(" -", file_path)

    if files:

        target_file = files[0]

        before = analyzer.get_file_before_commit(
            commit["hash"],
            target_file
        )

        after = analyzer.get_file_after_commit(
            commit["hash"],
            target_file
        )

        print(
            "\nTarget file:",
            target_file
        )

        print(
            "Pre-fix version available:",
            before is not None
        )

        print(
            "Post-fix version available:",
            after is not None
        )

    print("\nCommit statistics:")

    stats = analyzer.get_commit_stats(
        commit["hash"]
    )

    pprint(stats)