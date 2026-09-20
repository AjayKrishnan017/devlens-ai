import ast


class CodeAnalyzer:
    def __init__(self, code):
        self.code = code
        self.tree = None

    def parse_code(self):
        """Convert Python source code into an AST."""

        try:
            self.tree = ast.parse(self.code)

            return {
                "valid": True,
                "message": "Code parsed successfully"
            }

        except SyntaxError as error:
            return {
                "valid": False,
                "message": str(error)
            }

    def analyze_structure(self):
        """Extract basic structural information from the AST."""

        if self.tree is None:
            result = self.parse_code()

            if not result["valid"]:
                return result

        functions = []
        classes = []
        imports = []
        loops = 0
        conditionals = 0
        try_blocks = 0

        for node in ast.walk(self.tree):

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)

            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

            elif isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)

            elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                loops += 1

            elif isinstance(node, ast.If):
                conditionals += 1

            elif isinstance(node, ast.Try):
                try_blocks += 1

        return {
            "valid": True,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "metrics": {
                "function_count": len(functions),
                "class_count": len(classes),
                "loop_count": loops,
                "conditional_count": conditionals,
                "try_block_count": try_blocks
            }
        }