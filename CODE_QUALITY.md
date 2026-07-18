# Code Quality Framework: ArenaSync AI

This document details the code quality standards, practices, and automated auditing checks established inside the **ArenaSync AI** platform.

---

## 🔍 Core Philosophy

The codebase is built to follow production-grade software quality metrics, ensuring high **Readability**, **Maintainability**, **Security**, and **Efficiency**. To enforce these guidelines and prevent code rot, we implement an **Automated AST (Abstract Syntax Tree) Static Code Quality Audit** that executes alongside our primary test suites.

---

## ⚙️ Automated Quality Checks

All python modules in the `app/` directory are parsed using Python's standard `ast` module inside [tests/test_code_quality.py](file:///c:/Users/udayk/OneDrive/Desktop/Hackathons/ArenaSync-AI/tests/test_code_quality.py). The test validates the following strict rules:

### 1. Mandatory Docstring Coverage
- **Rule**: Every Python module, Class definition, and Function/Method definition must contain a docstring (`__doc__`).
- **Rationale**: Promotes developer onboarding and self-documenting code.
- **Example**:
  ```python
  def search_rag(query: str, limit: int = 3) -> str:
      """
      Search the local knowledge base using a token overlap ranking.
      Returns a formatted context string for LLM prompting.
      """
  ```

### 2. Modularity & Function Length Boundaries
- **Rule**: No function or method can exceed **60 lines of code**.
- **Rationale**: Keeps functions focused on a single responsibility, which improves unit-testability and maintains readability.

### 3. Cognitive Complexity Branching Index
- **Rule**: No function can exceed **10 branching blocks** (count of `if`, `for`, `while`, `except`, and boolean logic gates like `and`/`or`).
- **Rationale**: Highly nested or branching functions are hard to follow, prone to corner-case bugs, and represent bad design layout.

### 4. Logging Safety (No Print Statements)
- **Rule**: Raw `print()` statements are forbidden inside the core application.
- **Rationale**: Print outputs are unbuffered, lack standardized logs levels (debug, info, warning, error), cannot be routed to files or aggregation platforms, and represent debugging pollution.
- **Example**:
  ```python
  import logging
  logger = logging.getLogger(__name__)
  logger.info("Starting ArenaSync server...")
  ```

### 5. Strict Imports (No Wildcards)
- **Rule**: Wildcard imports (`from module import *`) are forbidden.
- **Rationale**: Wildcards pollute the local namespace, hide name conflicts, make tracing imports difficult, and slow down import evaluations.

### 6. Naming Style Standards
- **Rule**: 
  - Classes must use **CamelCase** (e.g. `GroqService`, `Settings`).
  - Functions, methods, and variables must use **snake_case** (e.g. `serve_home_page`, `audit_errors`).
- **Rationale**: Consistency with standard PEP 8 naming style variables.

---

## 🚀 Running the Code Quality Audit

The code quality check runs as a native `pytest` test case. To execute it:

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run the quality audit test
python -m pytest tests/test_code_quality.py -v
```

Every new commit or function added is parsed dynamically, guaranteeing that future developers cannot bypass style, length, or complexity rules.
