#!/usr/bin/env python3
"""
Constitutional Compliance Validator - Tier1 Workflow

Validates Tier1 projects against constitutional articles:
- Article II: Anti-Abstraction (detect unnecessary wrappers)
- Article IV: Contract-First (check for contract files when needed)
- Article VI: Observable Systems (check for CLI interfaces)

Article III (simulation detection) handled by detect_simulation_code.py

Usage:
    python3 validate_constitutional_compliance.py [--json] [--verbose]
    python3 validate_constitutional_compliance.py --article II

Exit codes:
    0 - Compliant or warnings only
    1 - Errors found (only in strict mode)
"""

import ast
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# Colorama for output (optional dependency)
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
    """Constitutional violation"""
    article: str  # "II", "IV", "VI"
    severity: str  # "warning" or "error"
    rule: str
    message: str
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    remediation: str = ""


@dataclass
class ValidationResult:
    """Validation result"""
    violations: List[Violation] = field(default_factory=list)
    files_scanned: int = 0
    articles_validated: List[str] = field(default_factory=list)

    @property
    def warnings(self) -> List[Violation]:
        return [v for v in self.violations if v.severity == "warning"]

    @property
    def errors(self) -> List[Violation]:
        return [v for v in self.violations if v.severity == "error"]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


class ConstitutionalValidator:
    """Validates Tier1 projects against constitution"""

    def __init__(self, project_root: Path, strict_mode: bool = False):
        self.project_root = project_root
        self.strict_mode = strict_mode
        self.result = ValidationResult()

    def validate(self, articles: Optional[List[str]] = None) -> ValidationResult:
        """Validate specified articles or all"""
        if articles is None:
            articles = ["II", "IV", "VI"]

        for article in articles:
            if article == "II":
                self._validate_article_ii()
            elif article == "IV":
                self._validate_article_iv()
            elif article == "VI":
                self._validate_article_vi()

        self.result.articles_validated = articles
        return self.result

    def _validate_article_ii(self):
        """Article II: Anti-Abstraction Principle"""
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return

        for py_file in src_dir.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            self.result.files_scanned += 1

            # Check for ignore directive
            if self._has_ignore_directive(py_file, "II"):
                continue

            # Detect wrapper classes
            violations = self._detect_wrappers(py_file)
            self.result.violations.extend(violations)

            # Detect redundant models
            violations = self._detect_redundant_models(py_file)
            self.result.violations.extend(violations)

    def _validate_article_iv(self):
        """Article IV: Contract-First"""
        # Check if project needs contracts (has MCP tools or APIs)
        needs_contracts = self._needs_contracts()

        if not needs_contracts:
            return  # Compliant by default

        # Check for contracts directory
        contracts_dir = self.project_root / "contracts"
        if not contracts_dir.exists():
            self.result.violations.append(Violation(
                article="IV",
                severity="warning",
                rule="contract-first",
                message="Project implements MCP tools/APIs but lacks contracts/ directory",
                remediation="Create contracts/ directory with JSON Schema contracts"
            ))

    def _validate_article_vi(self):
        """Article VI: Observable Systems"""
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return

        # Find service modules (files with classes or significant logic)
        services = self._find_service_modules(src_dir)

        for service in services:
            if self._has_ignore_directive(service, "VI"):
                continue

            # Check if has CLI interface
            has_cli = self._has_cli_interface(service)

            if not has_cli:
                self.result.violations.append(Violation(
                    article="VI",
                    severity="warning",
                    rule="observable-systems",
                    message=f"Service module lacks CLI interface: {service.name}",
                    file_path=service,
                    remediation="Add if __name__ == '__main__': block or cli.py file"
                ))

    # Helper methods

    def _should_skip(self, path: Path) -> bool:
        """Skip certain paths"""
        skip_patterns = ['__pycache__', '.venv', 'venv', 'node_modules', '.git', 'tests/']
        return any(pattern in str(path) for pattern in skip_patterns)

    def _has_ignore_directive(self, file_path: Path, article: str) -> bool:
        """Check for # tier1-constitution-ignore: article-X"""
        try:
            content = file_path.read_text()
            pattern = f"tier1-constitution-ignore:.*article-{article}"
            return bool(re.search(pattern, content, re.IGNORECASE))
        except:
            return False

    def _detect_wrappers(self, file_path: Path) -> List[Violation]:
        """Detect wrapper classes that just delegate"""
        violations = []
        try:
            tree = ast.parse(file_path.read_text())

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._is_simple_wrapper(node):
                        violations.append(Violation(
                            article="II",
                            severity="warning",
                            rule="anti-abstraction",
                            message=f"Possible unnecessary wrapper class: {node.name}",
                            file_path=file_path,
                            line_number=node.lineno,
                            remediation="Consider using framework/library directly"
                        ))
        except:
            pass

        return violations

    def _is_simple_wrapper(self, class_node: ast.ClassDef) -> bool:
        """Heuristic: class with only simple delegation methods"""
        if len(class_node.body) < 2:  # Too simple to be wrapper
            return False

        method_count = 0
        delegation_count = 0

        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_count += 1
                # Check if method just calls another function
                if self._is_simple_delegation(item):
                    delegation_count += 1

        # If >50% of methods are simple delegations, likely a wrapper
        if method_count > 0 and delegation_count / method_count > 0.5:
            return True

        return False

    def _is_simple_delegation(self, func_node: ast.FunctionDef) -> bool:
        """Check if function just delegates to another call"""
        if len(func_node.body) == 1:
            stmt = func_node.body[0]
            if isinstance(stmt, ast.Return):
                if isinstance(stmt.value, ast.Call):
                    return True
        return False

    def _detect_redundant_models(self, file_path: Path) -> List[Violation]:
        """Detect multiple models for same entity (User, UserDTO, UserModel, etc.)"""
        violations = []
        try:
            tree = ast.parse(file_path.read_text())

            # Extract class names
            class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            # Group by base name (User, UserDTO, UserResponse -> "user")
            base_names = {}
            for name in class_names:
                # Remove common suffixes
                base = re.sub(r'(DTO|Model|Schema|Response|Request|Entity)$', '', name, flags=re.IGNORECASE)
                base = base.lower()

                if base not in base_names:
                    base_names[base] = []
                base_names[base].append(name)

            # Check for redundancy (3+ models for same entity)
            for base, names in base_names.items():
                if len(names) >= 3:
                    violations.append(Violation(
                        article="II",
                        severity="warning",
                        rule="anti-abstraction",
                        message=f"Redundant models detected: {', '.join(names)}",
                        file_path=file_path,
                        remediation="Consider single model with optional fields (Pydantic defaults)"
                    ))
        except:
            pass

        return violations

    def _needs_contracts(self) -> bool:
        """Check if project implements MCP tools or APIs"""
        indicators = [
            "mcp.tool",
            "@app.post",
            "@app.get",
            "FastAPI",
            "GraphQL"
        ]

        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return False

        for py_file in src_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                if any(indicator in content for indicator in indicators):
                    return True
            except:
                pass

        return False

    def _find_service_modules(self, src_dir: Path) -> List[Path]:
        """Find modules that likely contain services (classes, significant logic)"""
        services = []

        for py_file in src_dir.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            # Skip __init__.py and very small files
            if py_file.name == "__init__.py":
                continue

            try:
                tree = ast.parse(py_file.read_text())

                # Check if has classes (likely a service)
                has_classes = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))

                # Check if has significant functions (>5 lines)
                has_logic = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if len(node.body) > 5:
                            has_logic = True
                            break

                if has_classes or has_logic:
                    services.append(py_file)
            except:
                pass

        return services

    def _has_cli_interface(self, file_path: Path) -> bool:
        """Check if file has CLI interface"""
        try:
            content = file_path.read_text()

            # Pattern 1: if __name__ == '__main__':
            if "if __name__ ==" in content:
                return True

            # Pattern 2: click decorators
            if "@click.command" in content:
                return True

            # Pattern 3: argparse
            if "argparse.ArgumentParser" in content:
                return True

            # Pattern 4: cli.py sibling file
            cli_file = file_path.parent / "cli.py"
            if cli_file.exists():
                return True

            return False
        except:
            return False


def print_report(result: ValidationResult, json_output: bool = False):
    """Print validation report"""
    if json_output:
        report = {
            "compliant": result.passed,
            "articles_validated": result.articles_validated,
            "files_scanned": result.files_scanned,
            "violations": [
                {
                    "article": v.article,
                    "severity": v.severity,
                    "rule": v.rule,
                    "message": v.message,
                    "file": str(v.file_path) if v.file_path else None,
                    "line": v.line_number,
                    "remediation": v.remediation
                }
                for v in result.violations
            ]
        }
        print(json.dumps(report, indent=2))
        return

    # Terminal output
    if not result.violations:
        print(f"{Fore.GREEN}✅ Constitutional compliance: PASSED{Style.RESET_ALL}")
        print(f"\nValidated articles: {', '.join(result.articles_validated)}")
        print(f"Files scanned: {result.files_scanned}")
        return

    print(f"{Fore.YELLOW}⚠️  Constitutional compliance: {len(result.violations)} violation(s){Style.RESET_ALL}\n")

    # Group by article
    by_article = {}
    for v in result.violations:
        if v.article not in by_article:
            by_article[v.article] = []
        by_article[v.article].append(v)

    for article, violations in sorted(by_article.items()):
        print(f"{Fore.CYAN}Article {article}:{Style.RESET_ALL}")
        for v in violations:
            severity_color = Fore.RED if v.severity == "error" else Fore.YELLOW
            location = f" at {v.file_path}:{v.line_number}" if v.file_path else ""
            print(f"  {severity_color}{v.severity.upper()}{Style.RESET_ALL}: {v.message}{location}")
            if v.remediation:
                print(f"    → {v.remediation}")
        print()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Tier1 constitutional compliance")
    parser.add_argument('--article', help='Validate specific article (II, IV, VI)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--strict', action='store_true', help='Strict mode (warnings become errors)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    project_root = Path.cwd()

    # Check for strict mode in config
    config_file = project_root / ".tier1_config.json"
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
            if config.get("constitutional_strict_mode"):
                args.strict = True
        except:
            pass

    validator = ConstitutionalValidator(project_root, strict_mode=args.strict)

    articles = [args.article] if args.article else None
    result = validator.validate(articles)

    print_report(result, json_output=args.json)

    # Exit code
    if args.strict and result.violations:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
