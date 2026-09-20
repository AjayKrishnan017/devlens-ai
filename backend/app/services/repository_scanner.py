from pathlib import Path

from app.services.feature_extractor import FeatureExtractor


class RepositoryScanner:

    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        ".tox",
        ".mypy_cache",
        ".pytest_cache"
    }

    def __init__(self, repository_path):
        self.repository_path = Path(repository_path)

    def should_ignore(self, path):
        return any(
            part in self.IGNORED_DIRECTORIES
            for part in path.parts
        )

    def find_python_files(self):
        files = []

        for path in self.repository_path.rglob("*.py"):

            if not self.should_ignore(path):
                files.append(path)

        return files

    def analyze_file(self, path):
        try:
            code = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            result = FeatureExtractor(code).extract()

            if not result["success"]:
                return None

            return {
                "file": str(
                    path.relative_to(self.repository_path)
                ),
                "features": result["features"]
            }

        except (OSError, UnicodeError):
            return None

    def scan(self):
        results = []

        for path in self.find_python_files():

            result = self.analyze_file(path)

            if result:
                results.append(result)

        return {
            "repository": self.repository_path.name,
            "files_analyzed": len(results),
            "results": results
        }