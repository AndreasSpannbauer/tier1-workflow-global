#!/usr/bin/env python3
"""
Simulation Code Detection Script

Detects patterns that indicate simulated/mocked implementations that should not exist
in production code. Part of the Agent Failure Reporting Protocol (EPIC-013 fix).

Usage:
    python3 detect_simulation_code.py <directory>
    python3 detect_simulation_code.py src/

Exit codes:
    0 - No simulation patterns detected
    1 - Simulation patterns detected (violations found)
    2 - Script error (invalid arguments, file access issues)
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


class SimulationPattern:
    """Represents a detected simulation pattern in code."""

    def __init__(self, file_path: str, line_number: int, pattern_type: str, context: str):
        self.file_path = file_path
        self.line_number = line_number
        self.pattern_type = pattern_type
        self.context = context

    def __str__(self) -> str:
        return f"❌ {self.file_path}\n  Line {self.line_number}: {self.pattern_type}\n    → {self.context}\n"


class SimulationDetector:
    """Detects simulation/mock patterns in Python source code."""

    # Pattern 1: Function names suggesting simulation
    SIMULATION_FUNCTION_PATTERNS = [
        r"def\s+_?simulate_",
        r"def\s+_?mock_",
        r"def\s+_?fake_",
        r"def\s+_?stub_",
        r"def\s+_?dummy_",
    ]

    # Pattern 2: Keyword-based conditional returns (hardcoded responses)
    KEYWORD_CONDITIONAL_PATTERN = r'if\s+["\'](\w+)["\']\s+in\s+\w+.*:\s*return\s+["\']'

    # Pattern 3: Suspicious TODO/FIXME comments
    SIMULATION_COMMENT_PATTERNS = [
        r"#.*TODO:?\s*replace.*real",
        r"#.*TODO:?\s*implement.*actual",
        r"#.*FIXME:?\s*simulation",
        r"#.*FIXME:?\s*mock",
        r"#.*placeholder.*implementation",
        r"#.*fake.*response",
    ]

    def __init__(self):
        self.violations: List[SimulationPattern] = []

    def detect_in_file(self, file_path: Path) -> List[SimulationPattern]:
        """Detect simulation patterns in a single Python file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            violations = []

            # Pattern 1: Function name detection
            for i, line in enumerate(lines, start=1):
                for pattern in self.SIMULATION_FUNCTION_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append(SimulationPattern(
                            file_path=str(file_path),
                            line_number=i,
                            pattern_type="Simulation function name",
                            context=line.strip()[:80]
                        ))

            # Pattern 2: Keyword-based conditional returns
            for i, line in enumerate(lines, start=1):
                match = re.search(self.KEYWORD_CONDITIONAL_PATTERN, line, re.IGNORECASE)
                if match:
                    violations.append(SimulationPattern(
                        file_path=str(file_path),
                        line_number=i,
                        pattern_type="Keyword-based conditional return",
                        context=line.strip()[:80]
                    ))

            # Pattern 3: Suspicious comments
            for i, line in enumerate(lines, start=1):
                for pattern in self.SIMULATION_COMMENT_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append(SimulationPattern(
                            file_path=str(file_path),
                            line_number=i,
                            pattern_type="Suspicious TODO/FIXME comment",
                            context=line.strip()[:80]
                        ))

            # Pattern 4: AST-based detection (detect hardcoded return values in conditionals)
            try:
                tree = ast.parse(content, filename=str(file_path))
                ast_violations = self._detect_ast_patterns(tree, str(file_path))
                violations.extend(ast_violations)
            except SyntaxError:
                # Skip files with syntax errors (they'll fail validation anyway)
                pass

            return violations

        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}", file=sys.stderr)
            return []

    def _detect_ast_patterns(self, tree: ast.AST, file_path: str) -> List[SimulationPattern]:
        """Use AST to detect deeper simulation patterns."""
        violations = []

        for node in ast.walk(tree):
            # Detect pattern: if "keyword" in var: return "hardcoded"
            if isinstance(node, ast.If):
                test = node.test
                # Check if it's a membership test (x in y)
                if isinstance(test, ast.Compare) and any(isinstance(op, ast.In) for op in test.ops):
                    # Check if the left side is a string constant
                    if isinstance(test.left, ast.Constant) and isinstance(test.left.value, str):
                        # Check if body contains a return with a string constant
                        for stmt in node.body:
                            if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant):
                                if isinstance(stmt.value.value, str):
                                    violations.append(SimulationPattern(
                                        file_path=file_path,
                                        line_number=node.lineno,
                                        pattern_type="AST: Keyword-conditional hardcoded return",
                                        context=f"if '{test.left.value}' in <var>: return '{stmt.value.value}'"
                                    ))

        return violations

    def scan_directory(self, directory: Path) -> Dict[str, List[SimulationPattern]]:
        """Scan all Python files in a directory recursively."""
        results = {}

        # Find all Python files
        python_files = list(directory.rglob("*.py"))

        for py_file in python_files:
            # Skip virtual environments and common non-source directories
            if any(part in py_file.parts for part in ['.venv', 'venv', '__pycache__', '.git', 'node_modules']):
                continue

            violations = self.detect_in_file(py_file)
            if violations:
                results[str(py_file)] = violations

        return results

    def print_report(self, results: Dict[str, List[SimulationPattern]]) -> None:
        """Print a formatted report of detected violations."""
        total_violations = sum(len(v) for v in results.values())

        if total_violations == 0:
            print("✅ No simulation patterns detected")
            print("")
            print("All code appears to use real implementations.")
            print("Agent Failure Reporting Protocol: PASSING")
            return

        print(f"❌ Detected {total_violations} simulation pattern(s) in {len(results)} file(s)")
        print("")
        print("Simulation patterns indicate code that SHOULD NOT EXIST:")
        print("- Mock/stub implementations that simulate real functionality")
        print("- Hardcoded responses based on input keywords")
        print("- Placeholder implementations with TODOs")
        print("")
        print("These patterns violate the Agent Failure Reporting Protocol.")
        print("Agents should have reported blockers instead of creating simulations.")
        print("")
        print("=" * 70)
        print("")

        for file_path, violations in sorted(results.items()):
            print(f"📄 {file_path}")
            print(f"   {len(violations)} violation(s)")
            print("")

            for violation in violations:
                print(f"   Line {violation.line_number}: {violation.pattern_type}")
                print(f"     → {violation.context}")
                print("")

        print("=" * 70)
        print("")
        print("Action required:")
        print("1. Review each violation to determine if it's a legitimate simulation")
        print("2. For test files: Ensure mocks are properly marked and isolated")
        print("3. For source files: Replace simulations with real implementations")
        print("4. If blocked: Use Agent Failure Reporting Protocol to report blocker")
        print("")


def main():
    """Main entry point for simulation detection."""
    if len(sys.argv) != 2:
        print("Usage: python3 detect_simulation_code.py <directory>", file=sys.stderr)
        print("Example: python3 detect_simulation_code.py src/", file=sys.stderr)
        sys.exit(2)

    directory_path = Path(sys.argv[1])

    if not directory_path.exists():
        print(f"Error: Directory '{directory_path}' does not exist", file=sys.stderr)
        sys.exit(2)

    if not directory_path.is_dir():
        print(f"Error: '{directory_path}' is not a directory", file=sys.stderr)
        sys.exit(2)

    print(f"🔍 Scanning {directory_path} for simulation patterns...")
    print("")

    detector = SimulationDetector()
    results = detector.scan_directory(directory_path)

    detector.print_report(results)

    # Exit with code 1 if violations found, 0 if clean
    total_violations = sum(len(v) for v in results.values())
    sys.exit(1 if total_violations > 0 else 0)


if __name__ == "__main__":
    main()
