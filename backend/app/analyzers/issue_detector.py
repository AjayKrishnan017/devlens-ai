import ast


class IssueDetector:
    def __init__(self, code):
        self.code = code
        self.tree = None
        self.issues = []

    def parse_code(self):
        try:
            self.tree = ast.parse(self.code)
            return True

        except SyntaxError as error:
            self.issues.append({
                "type": "SYNTAX_ERROR",
                "severity": "HIGH",
                "line": error.lineno,
                "message": error.msg
            })

            return False

    def add_issue(self, issue_type, severity, line, message):
        self.issues.append({
            "type": issue_type,
            "severity": severity,
            "line": line,
            "message": message
        })

    def detect_bare_except(self):
        for node in ast.walk(self.tree):

            if isinstance(node, ast.ExceptHandler):

                if node.type is None:
                    self.add_issue(
                        "BARE_EXCEPT",
                        "MEDIUM",
                        node.lineno,
                        "Bare except catches every exception."
                    )

    def detect_empty_except(self):
        for node in ast.walk(self.tree):

            if isinstance(node, ast.ExceptHandler):

                if (
                    len(node.body) == 1
                    and isinstance(node.body[0], ast.Pass)
                ):
                    self.add_issue(
                        "EMPTY_EXCEPT",
                        "HIGH",
                        node.lineno,
                        "Exception is ignored using pass."
                    )

    def detect_dangerous_functions(self):
        for node in ast.walk(self.tree):

            if isinstance(node, ast.Call):

                if isinstance(node.func, ast.Name):

                    if node.func.id == "eval":
                        self.add_issue(
                            "DANGEROUS_EVAL",
                            "HIGH",
                            node.lineno,
                            "eval() can execute arbitrary Python expressions."
                        )

                    elif node.func.id == "exec":
                        self.add_issue(
                            "DANGEROUS_EXEC",
                            "HIGH",
                            node.lineno,
                            "exec() can execute arbitrary Python code."
                        )

    def detect_mutable_defaults(self):
        for node in ast.walk(self.tree):

            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):

                defaults = (
                    list(node.args.defaults)
                    + [
                        default
                        for default in node.args.kw_defaults
                        if default is not None
                    ]
                )

                for default in defaults:

                    if isinstance(
                        default,
                        (ast.List, ast.Dict, ast.Set)
                    ):
                        self.add_issue(
                            "MUTABLE_DEFAULT",
                            "MEDIUM",
                            node.lineno,
                            f"Function '{node.name}' uses a mutable default argument."
                        )

    def detect_wildcard_imports(self):
        for node in ast.walk(self.tree):

            if isinstance(node, ast.ImportFrom):

                for alias in node.names:

                    if alias.name == "*":
                        self.add_issue(
                            "WILDCARD_IMPORT",
                            "LOW",
                            node.lineno,
                            "Wildcard imports can make code harder to understand."
                        )

    def detect_todos(self):
        for line_number, line in enumerate(
            self.code.splitlines(),
            start=1
        ):

            if "TODO" in line.upper():
                self.add_issue(
                    "TODO_FOUND",
                    "LOW",
                    line_number,
                    "Unresolved TODO found in source code."
                )

    def analyze(self):
        self.issues = []

        if not self.parse_code():
            return self.issues

        self.detect_bare_except()
        self.detect_empty_except()
        self.detect_dangerous_functions()
        self.detect_mutable_defaults()
        self.detect_wildcard_imports()
        self.detect_todos()

        return self.issues