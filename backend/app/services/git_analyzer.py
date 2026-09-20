import re
import subprocess
from pathlib import Path
from typing import Optional


class GitAnalyzer:
    """
    Analyze the Git history of a local repository.

    Used by DevLens to:
    - inspect commits
    - identify potential bug-fix commits
    - find changed Python files
    - retrieve source code before/after a commit
    - obtain commit metadata
    """

    BUG_KEYWORDS = {
        "fix",
        "fixed",
        "fixes",
        "bug",
        "bugfix",
        "defect",
        "regression",
        "crash",
        "incorrect",
        "error",
        "fault",
        "issue",
    }

    def __init__(self, repository_path):
        self.repository_path = Path(repository_path).resolve()

        if not self.repository_path.exists():
            raise ValueError(
                f"Repository does not exist: "
                f"{self.repository_path}"
            )

        if not self.repository_path.is_dir():
            raise ValueError(
                f"Repository path is not a directory: "
                f"{self.repository_path}"
            )

        git_directory = self.repository_path / ".git"

        if not git_directory.exists():
            raise ValueError(
                f"Not a Git repository: "
                f"{self.repository_path}"
            )

    # ---------------------------------------------------------
    # Git command execution
    # ---------------------------------------------------------

    def run_git(self, *args):
        """
        Execute a Git command inside the repository.
        """

        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                check=False,
            )

        except FileNotFoundError as error:
            raise RuntimeError(
                "Git executable was not found. "
                "Make sure Git is installed and available in PATH."
            ) from error

        if result.returncode != 0:
            command = "git " + " ".join(args)

            error_message = (
                result.stderr.strip()
                or result.stdout.strip()
                or "Unknown Git error"
            )

            raise RuntimeError(
                f"Git command failed:\n"
                f"{command}\n\n"
                f"{error_message}"
            )

        return result.stdout

    # ---------------------------------------------------------
    # Bug-fix detection
    # ---------------------------------------------------------

    def is_bug_fix_message(self, message):
        """
        Heuristically determine whether a commit message
        appears to describe a bug fix.

        This is NOT perfect ground truth.
        """

        normalized = message.lower()

        words = set(
            re.findall(
                r"[a-zA-Z]+",
                normalized
            )
        )

        return bool(
            words.intersection(self.BUG_KEYWORDS)
        )

    # ---------------------------------------------------------
    # Commit collection
    # ---------------------------------------------------------

    def get_commits(self, limit=500):
        """
        Return recent commits and basic metadata.
        """

        if limit <= 0:
            return []

        output = self.run_git(
            "log",
            f"-n{limit}",
            "--pretty=format:%H%x09%P%x09%an%x09%ad%x09%s",
            "--date=iso-strict",
        )

        commits = []

        for line in output.splitlines():

            parts = line.split("\t", 4)

            if len(parts) != 5:
                continue

            (
                commit_hash,
                parents,
                author,
                date,
                message,
            ) = parts

            parent_hashes = (
                parents.split()
                if parents
                else []
            )

            commits.append({
                "hash": commit_hash,
                "parents": parent_hashes,
                "author": author,
                "date": date,
                "message": message,
                "bug_fix": self.is_bug_fix_message(
                    message
                ),
            })

        return commits

    # ---------------------------------------------------------
    # Single commit metadata
    # ---------------------------------------------------------

    def get_commit(self, commit_hash):
        """
        Return metadata for one commit.
        """

        output = self.run_git(
            "show",
            "-s",
            "--pretty=format:%H%x09%P%x09%an%x09%ad%x09%s",
            "--date=iso-strict",
            commit_hash,
        )

        parts = output.strip().split("\t", 4)

        if len(parts) != 5:
            return None

        (
            commit_hash,
            parents,
            author,
            date,
            message,
        ) = parts

        return {
            "hash": commit_hash,
            "parents": (
                parents.split()
                if parents
                else []
            ),
            "author": author,
            "date": date,
            "message": message,
            "bug_fix": self.is_bug_fix_message(
                message
            ),
        }

    # ---------------------------------------------------------
    # Parent commit
    # ---------------------------------------------------------

    def get_parent_commit(
        self,
        commit_hash
    ) -> Optional[str]:
        """
        Return the first parent of a commit.

        For merge commits, only the first parent is used.
        """

        commit = self.get_commit(
            commit_hash
        )

        if not commit:
            return None

        parents = commit["parents"]

        if not parents:
            return None

        return parents[0]

    # ---------------------------------------------------------
    # Changed files
    # ---------------------------------------------------------

    def get_changed_files(
        self,
        commit_hash
    ):
        """
        Return all files changed by a commit.
        """

        output = self.run_git(
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            commit_hash,
        )

        files = [
            line.strip()
            for line in output.splitlines()
            if line.strip()
        ]

        return sorted(set(files))

    def get_changed_python_files(
        self,
        commit_hash
    ):
        """
        Return Python files changed by a commit.
        """

        files = self.get_changed_files(
            commit_hash
        )

        return [
            file_path
            for file_path in files
            if file_path.lower().endswith(".py")
        ]

    # ---------------------------------------------------------
    # File retrieval
    # ---------------------------------------------------------

    def get_file_at_commit(
        self,
        commit_hash,
        file_path
    ) -> Optional[str]:
        """
        Return a file exactly as it existed at a commit.
        """

        try:
            return self.run_git(
                "show",
                f"{commit_hash}:{file_path}"
            )

        except RuntimeError:
            return None

    def get_file_before_commit(
        self,
        commit_hash,
        file_path
    ) -> Optional[str]:
        """
        Return a file as it existed immediately BEFORE
        the specified commit.

        This is useful for obtaining the potentially
        defective version before a bug-fix commit.
        """

        parent = self.get_parent_commit(
            commit_hash
        )

        if parent is None:
            return None

        return self.get_file_at_commit(
            parent,
            file_path
        )

    def get_file_after_commit(
        self,
        commit_hash,
        file_path
    ) -> Optional[str]:
        """
        Return the version of a file AFTER the commit.
        """

        return self.get_file_at_commit(
            commit_hash,
            file_path
        )

    # ---------------------------------------------------------
    # Commit statistics
    # ---------------------------------------------------------

    def get_commit_stats(
        self,
        commit_hash
    ):
        """
        Return insertion/deletion statistics for a commit.
        """

        output = self.run_git(
            "show",
            "--numstat",
            "--format=",
            commit_hash,
        )

        files = []

        total_added = 0
        total_deleted = 0

        for line in output.splitlines():

            parts = line.split("\t")

            if len(parts) != 3:
                continue

            added, deleted, path = parts

            # Binary files show "-" instead of numbers.
            try:
                added_count = int(added)
            except ValueError:
                added_count = 0

            try:
                deleted_count = int(deleted)
            except ValueError:
                deleted_count = 0

            total_added += added_count
            total_deleted += deleted_count

            files.append({
                "file": path,
                "added": added_count,
                "deleted": deleted_count,
            })

        return {
            "files_changed": len(files),
            "lines_added": total_added,
            "lines_deleted": total_deleted,
            "files": files,
        }

    # ---------------------------------------------------------
    # Bug-fix commits
    # ---------------------------------------------------------

    def get_bug_fix_commits(
        self,
        limit=500
    ):
        """
        Return commits whose messages match our
        bug-fix heuristic.
        """

        commits = self.get_commits(
            limit=limit
        )

        return [
            commit
            for commit in commits
            if commit["bug_fix"]
        ]

    # ---------------------------------------------------------
    # Repository summary
    # ---------------------------------------------------------

    def get_repository_summary(
        self,
        commit_limit=500
    ):
        """
        Generate basic Git-history statistics.
        """

        commits = self.get_commits(
            limit=commit_limit
        )

        bug_fix_commits = [
            commit
            for commit in commits
            if commit["bug_fix"]
        ]

        python_files_changed = set()

        for commit in bug_fix_commits:

            files = self.get_changed_python_files(
                commit["hash"]
            )

            python_files_changed.update(
                files
            )

        return {
            "repository": self.repository_path.name,
            "repository_path": str(
                self.repository_path
            ),
            "commits_scanned": len(commits),
            "potential_bug_fix_commits": len(
                bug_fix_commits
            ),
            "python_files_touched_by_bug_fixes": len(
                python_files_changed
            ),
        }