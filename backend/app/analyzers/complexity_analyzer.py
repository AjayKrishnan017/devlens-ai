import ast


class ComplexityAnalyzer:

    COMPLEXITY_NODES = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.ExceptHandler,
        ast.IfExp,
    )

    NESTING_NODES = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.Try,
        ast.With,
        ast.AsyncWith,
    )

    def __init__(self, code):
        self.code = code
        self.tree = None

    def parse(self):
        try:
            self.tree = ast.parse(self.code)
            return True
        except SyntaxError:
            return False

    def calculate_complexity(self, function_node):
        complexity = 1

        for node in ast.walk(function_node):

            if isinstance(node, self.COMPLEXITY_NODES):
                complexity += 1

            elif isinstance(node, ast.BoolOp):
                complexity += max(len(node.values) - 1, 0)

        return complexity

    def count_parameters(self, function_node):
        args = function_node.args

        total = (
            len(args.posonlyargs)
            + len(args.args)
            + len(args.kwonlyargs)
        )

        if args.vararg:
            total += 1

        if args.kwarg:
            total += 1

        # Don't count self/cls as normal parameters.
        if args.args and args.args[0].arg in {"self", "cls"}:
            total -= 1

        return total

    def function_length(self, function_node):
        end_line = getattr(
            function_node,
            "end_lineno",
            function_node.lineno
        )

        return end_line - function_node.lineno + 1

    def calculate_nesting(self, function_node):

        max_depth = 0

        def visit(node, depth):
            nonlocal max_depth

            next_depth = depth

            if isinstance(node, self.NESTING_NODES):
                next_depth += 1
                max_depth = max(max_depth, next_depth)

            for child in ast.iter_child_nodes(node):
                visit(child, next_depth)

        # Start from the contents so the function itself isn't nesting.
        for child in function_node.body:
            visit(child, 0)

        return max_depth

    def get_risk(self, complexity):

        if complexity <= 5:
            return "LOW"

        if complexity <= 10:
            return "MEDIUM"

        if complexity <= 20:
            return "HIGH"

        return "VERY_HIGH"

    def analyze(self):

        if not self.parse():
            return {
                "success": False,
                "functions": []
            }

        functions = []

        for node in ast.walk(self.tree):

            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):

                complexity = self.calculate_complexity(node)
                parameter_count = self.count_parameters(node)
                length = self.function_length(node)
                nesting_depth = self.calculate_nesting(node)

                warnings = []

                if complexity > 10:
                    warnings.append(
                        "Function has high cyclomatic complexity."
                    )

                if parameter_count > 5:
                    warnings.append(
                        "Function has too many parameters."
                    )

                if length > 50:
                    warnings.append(
                        "Function is very long."
                    )

                if nesting_depth > 4:
                    warnings.append(
                        "Function has deep nesting."
                    )

                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "complexity": complexity,
                    "risk": self.get_risk(complexity),
                    "parameters": parameter_count,
                    "length": length,
                    "nesting_depth": nesting_depth,
                    "warnings": warnings
                })

        return {
            "success": True,
            "function_count": len(functions),
            "functions": functions
        }