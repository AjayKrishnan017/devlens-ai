from pprint import pprint

from app.services.repository_scanner import RepositoryScanner


scanner = RepositoryScanner(".")

report = scanner.scan()

print(
    f"Repository: {report['repository']}"
)

print(
    f"Python files analyzed: {report['files_analyzed']}"
)

print("\nFILES\n")

for result in report["results"]:

    print(result["file"])

    pprint(result["features"])

    print("-" * 60)