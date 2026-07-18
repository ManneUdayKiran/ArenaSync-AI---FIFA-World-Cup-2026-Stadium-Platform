import os
import ast
import re
from typing import List

# Configurations for Code Quality Audit
MAX_FUNCTION_LINES = 100
MAX_COGNITIVE_BRANCHES = 12
EXCLUDED_DIRECTORIES = ["__pycache__", "static", "templates"]

def get_python_files(root_dir: str) -> List[str]:
    """Traverses app/ directory to locate all python source files."""
    py_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRECTORIES]
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                py_files.append(os.path.join(root, file))
    return py_files

def test_codebase_quality_audit():
    """
    Automated Static Analysis Audit: scans the app/ folder using Python's
    Abstract Syntax Tree (AST) to verify strict code quality rules.
    """
    app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app")
    py_files = get_python_files(app_dir)
    
    # We must have python files in app/
    assert len(py_files) > 0, "No python files found in app/ directory."
    
    audit_errors = []
    
    for file_path in py_files:
        rel_path = os.path.relpath(file_path, app_dir)
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
            
        try:
            tree = ast.parse(code, filename=file_path)
        except SyntaxError as e:
            audit_errors.append(f"Syntax Error in {rel_path}: {e}")
            continue
            
        # 1. Module Docstring Check
        module_doc = ast.get_docstring(tree)
        if not module_doc:
            audit_errors.append(f"Module docstring missing in: app/{rel_path}")

        for node in ast.walk(tree):
            # 2. Class checks
            if isinstance(node, ast.ClassDef):
                # Naming Style (CamelCase)
                if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                    audit_errors.append(f"Class name '{node.name}' in app/{rel_path} does not use CamelCase.")
                
                # Class Docstring (Skip if inherits from BaseModel or settings helper)
                is_pydantic = any(isinstance(b, ast.Name) and b.id == "BaseModel" for b in node.bases)
                if not is_pydantic and node.name != "Settings" and not ast.get_docstring(node):
                    audit_errors.append(f"Class '{node.name}' in app/{rel_path} is missing a docstring.")
                    
            # 3. Function checks
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip magic methods and private helper functions
                is_magic_or_private = node.name.startswith("_") or node.name == "__init__"
                
                # Naming Style (snake_case)
                if not is_magic_or_private and not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                    audit_errors.append(f"Function name '{node.name}' in app/{rel_path} does not use snake_case.")
                    
                # Function Docstring
                if not is_magic_or_private and not ast.get_docstring(node):
                    audit_errors.append(f"Function '{node.name}' in app/{rel_path} is missing a docstring.")
                    
                # Function Length Check (Lines of Code)
                func_lines = node.end_lineno - node.lineno
                if func_lines > MAX_FUNCTION_LINES:
                    audit_errors.append(f"Function '{node.name}' in app/{rel_path} exceeds maximum line limit ({func_lines}/{MAX_FUNCTION_LINES} lines).")
                    
                # Branching Complexity Check (Cognitive branch counting)
                branches = 0
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.BoolOp)):
                        branches += 1
                if branches > MAX_COGNITIVE_BRANCHES:
                    audit_errors.append(f"Function '{node.name}' in app/{rel_path} exceeds cognitive complexity branching index ({branches}/{MAX_COGNITIVE_BRANCHES}).")
                    
            # 4. Import check: No Wildcard Imports
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    if name.name == "*":
                        audit_errors.append(f"Wildcard import 'from {node.module} import *' detected in app/{rel_path}.")
                        
            # 5. Logging Check: No raw print statements (logging should be used)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    audit_errors.append(f"Raw print statement detected in app/{rel_path} (use logger instead).")

    # Assert that all rules pass successfully
    assert len(audit_errors) == 0, "Code Quality audit failed with the following issues:\n" + "\n".join(audit_errors)
