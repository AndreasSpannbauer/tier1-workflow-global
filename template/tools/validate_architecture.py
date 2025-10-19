#!/usr/bin/env python3
"""
Architecture Validation Script

MIT License - Copy and customize for your project

USAGE:
    python validate_architecture.py [--config CONFIG] [--json] [--verbose]

CUSTOMIZATION:
    1. Edit RULES dict to match your project's architecture
    2. Add custom validators in validate_* functions
    3. Update module_patterns to match your directory structure
    4. Adjust severity levels (error/warning)

EXAMPLE CONFIG (architecture_rules.json):
    {
        "module_patterns": {
            "backend": "^(src|lib)/backend/",
            "frontend": "^(src|lib)/frontend/",
            "database": "^(src|lib)/db/"
        },
        "forbidden_imports": [
            {"from": "backend", "to": "frontend", "reason": "Backend cannot import frontend"},
            {"from": "frontend", "to": "database", "reason": "Frontend must use API, not direct DB"}
        ],
        "required_boundaries": ["api", "domain", "infrastructure"]
    }
"""

import argparse
import ast
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Optional colorized output (graceful fallback)
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = CYAN = ""
    class Style:
        RESET_ALL = BRIGHT = ""
    HAS_COLOR = False


@dataclass
class Violation:
    """Architecture violation"""
    severity: str  # 'error' or 'warning'
    rule: str
    message: str
    file_path: Optional[Path] = None
    line_number: Optional[int] = None

    def __str__(self) -> str:
        prefix = f"{Fore.RED}ERROR" if self.severity == 'error' else f"{Fore.YELLOW}WARNING"
        location = f" at {self.file_path}:{self.line_number}" if self.file_path else ""
        return f"{prefix}{Style.RESET_ALL}: [{self.rule}] {self.message}{location}"


@dataclass
class ValidationResult:
    """Validation result container"""
    violations: List[Violation] = field(default_factory=list)
    files_scanned: int = 0

    @property
    def errors(self) -> List[Violation]:
        return [v for v in self.violations if v.severity == 'error']

    @property
    def warnings(self) -> List[Violation]:
        return [v for v in self.violations if v.severity == 'warning']

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


# DEFAULT RULES - Customize these for your project
DEFAULT_RULES = {
    "module_patterns": {
        # Map module names to regex patterns matching file paths
        "backend": r"^(src|lib)/backend/",
        "frontend": r"^(src|lib)/frontend/",
        "database": r"^(src|lib)/(db|database|models)/",
        "api": r"^(src|lib)/api/",
        "utils": r"^(src|lib)/(utils|common)/",
    },
    "forbidden_imports": [
        # Prevent architectural violations
        {"from": "frontend", "to": "backend", "reason": "Frontend cannot import backend (use API)"},
        {"from": "frontend", "to": "database", "reason": "Frontend cannot access database directly"},
        {"from": "backend", "to": "frontend", "reason": "Backend cannot import frontend code"},
        {"from": "api", "to": "frontend", "reason": "API layer cannot import frontend"},
    ],
    "circular_dependency_check": True,
    "max_module_depth": 5,  # Warn if module nesting exceeds this
}


class ArchitectureValidator:
    """Main validation engine"""

    def __init__(self, root_dir: Path, rules: Dict[str, Any], verbose: bool = False):
        self.root_dir = root_dir.resolve()
        self.rules = rules
        self.verbose = verbose
        self.result = ValidationResult()

        # Dependency graph for circular dependency detection
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)

    def log(self, message: str) -> None:
        """Verbose logging"""
        if self.verbose:
            print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}")

    def validate(self) -> ValidationResult:
        """Run all validation checks"""
        self.log(f"Scanning Python files in {self.root_dir}")

        python_files = list(self.root_dir.rglob("*.py"))
        self.result.files_scanned = len(python_files)

        # Build dependency graph
        for file_path in python_files:
            self._scan_file_imports(file_path)

        # Run validation checks
        self._validate_forbidden_imports()

        if self.rules.get("circular_dependency_check", True):
            self._validate_circular_dependencies()

        self._validate_module_depth()

        return self.result

    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name"""
        try:
            rel_path = file_path.relative_to(self.root_dir)
            # Remove .py extension and convert path to module notation
            module = str(rel_path.with_suffix('')).replace('/', '.')
            return module
        except ValueError:
            return str(file_path)

    def _get_module_type(self, file_path: Path) -> Optional[str]:
        """Determine module type based on path patterns"""
        rel_path = str(file_path.relative_to(self.root_dir))

        for module_name, pattern in self.rules.get("module_patterns", {}).items():
            if re.match(pattern, rel_path):
                return module_name

        return None

    def _scan_file_imports(self, file_path: Path) -> None:
        """Extract imports from Python file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))

            module_name = self._get_module_name(file_path)

            for node in ast.walk(tree):
                imported_modules = []

                if isinstance(node, ast.Import):
                    imported_modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_modules = [node.module]

                for imported in imported_modules:
                    # Store dependency
                    self.dependencies[module_name].add(imported)

        except (SyntaxError, UnicodeDecodeError) as e:
            self.result.violations.append(Violation(
                severity='warning',
                rule='parse_error',
                message=f"Failed to parse file: {e}",
                file_path=file_path
            ))

    def _validate_forbidden_imports(self) -> None:
        """Check for forbidden import patterns"""
        self.log("Checking forbidden imports")

        forbidden = self.rules.get("forbidden_imports", [])

        for module, imports in self.dependencies.items():
            # Find module file
            module_path = self.root_dir / module.replace('.', '/')
            if not module_path.exists():
                module_path = module_path.parent / (module_path.name + '.py')

            from_type = self._get_module_type(module_path) if module_path.exists() else None

            for imported in imports:
                # Find imported module file
                imported_path = self.root_dir / imported.replace('.', '/')
                if not imported_path.exists():
                    imported_path = imported_path.parent / (imported_path.name + '.py')

                to_type = self._get_module_type(imported_path) if imported_path.exists() else None

                # Check forbidden rules
                for rule in forbidden:
                    if from_type == rule['from'] and to_type == rule['to']:
                        self.result.violations.append(Violation(
                            severity='error',
                            rule='forbidden_import',
                            message=f"{rule['reason']}: {module} imports {imported}",
                            file_path=module_path
                        ))

    def _validate_circular_dependencies(self) -> None:
        """Detect circular dependencies"""
        self.log("Checking circular dependencies")

        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(module: str, path: List[str]) -> None:
            if module in stack:
                # Circular dependency found
                cycle_start = path.index(module)
                cycle = path[cycle_start:] + [module]
                self.result.violations.append(Violation(
                    severity='error',
                    rule='circular_dependency',
                    message=f"Circular dependency: {' -> '.join(cycle)}"
                ))
                return

            if module in visited:
                return

            visited.add(module)
            stack.add(module)

            for dep in self.dependencies.get(module, []):
                dfs(dep, path + [module])

            stack.remove(module)

        for module in self.dependencies:
            dfs(module, [])

    def _validate_module_depth(self) -> None:
        """Check module nesting depth"""
        max_depth = self.rules.get("max_module_depth", 5)

        for module in self.dependencies:
            depth = module.count('.')
            if depth > max_depth:
                module_path = self.root_dir / module.replace('.', '/')
                if not module_path.exists():
                    module_path = module_path.parent / (module_path.name + '.py')

                self.result.violations.append(Violation(
                    severity='warning',
                    rule='module_depth',
                    message=f"Module nesting too deep ({depth} > {max_depth}): {module}",
                    file_path=module_path
                ))


def load_config(config_path: Optional[Path]) -> Dict[str, Any]:
    """Load configuration from JSON file or use defaults"""
    if config_path and config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_RULES


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate project architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "root_dir",
        type=Path,
        nargs='?',
        default=Path.cwd(),
        help="Root directory to validate (default: current directory)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to architecture rules config (JSON)"
    )
    parser.add_argument(
        "--json",
        action='store_true',
        help="Output results as JSON"
    )
    parser.add_argument(
        "--verbose",
        action='store_true',
        help="Verbose output"
    )

    args = parser.parse_args()

    # Load rules
    rules = load_config(args.config)

    # Run validation
    validator = ArchitectureValidator(args.root_dir, rules, verbose=args.verbose)
    result = validator.validate()

    # Output results
    if args.json:
        output = {
            "passed": result.passed,
            "files_scanned": result.files_scanned,
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "violations": [
                {
                    "severity": v.severity,
                    "rule": v.rule,
                    "message": v.message,
                    "file": str(v.file_path) if v.file_path else None,
                    "line": v.line_number
                }
                for v in result.violations
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print(f"\n{Fore.CYAN}Architecture Validation{Style.RESET_ALL}")
        print(f"Files scanned: {result.files_scanned}")
        print(f"Errors: {Fore.RED if result.errors else Fore.GREEN}{len(result.errors)}{Style.RESET_ALL}")
        print(f"Warnings: {Fore.YELLOW if result.warnings else Fore.GREEN}{len(result.warnings)}{Style.RESET_ALL}")

        if result.violations:
            print(f"\n{Style.BRIGHT}Violations:{Style.RESET_ALL}")
            for violation in result.violations:
                print(f"  {violation}")

        if result.passed:
            print(f"\n{Fore.GREEN}✓ Architecture validation passed{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}✗ Architecture validation failed{Style.RESET_ALL}")

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
