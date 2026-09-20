from app.services.git_analyzer import GitAnalyzer


repo = "../repositories/flask"

analyzer = GitAnalyzer(repo)

commits = analyzer.get_commits(limit=100)

bug_fixes = [
    commit
    for commit in commits
    if commit["bug_fix"]
]


print(f"Commits scanned: {len(commits)}")
print(f"Potential bug-fix commits: {len(bug_fixes)}")

print("\nPotential bug fixes:\n")


for commit in bug_fixes[:10]:

    print(commit["hash"][:8], commit["message"])

    files = analyzer.get_changed_python_files(
        commit["hash"]
    )

    for file in files[:5]:
        print("   ->", file)

    print()