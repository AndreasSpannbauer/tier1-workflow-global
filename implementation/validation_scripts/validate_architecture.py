#!/usr/bin/env python3
"""
Architecture Validation Template

PURPOSE: Enforce architectural boundaries in your codebase

CUSTOMIZE THIS FILE for your project:
- Update LAYER_DEPENDENCIES to match your architecture
- Update FORBIDDEN_PATTERNS to enforce your rules
- Update file paths to match your project structure

EXAMPLE: Layered architecture (Clean Architecture, Hexagonal Architecture)
- Domain layer should not import infrastructure layer
- Application layer can import domain layer
- Infrastructure layer can import domain and application layers

This is a TEMPLATE - adapt it to your project's needs.
"""

import sys
from pathlib import Path
from typing import Dict, List, Set
import re

# ==============================================================================
# CUSTOMIZE THESE FOR YOUR PROJECT
# ==============================================================================

# Define your project's layer structure and allowed dependencies
# Format: {layer: {allowed_dependency_layers}}
LAYER_DEPENDENCIES: Dict[str, Set[str]] = {
    "domain": set(),  # Domain depends on nothing
    "application": {"domain"},  # Application can use domain
    "infrastructure": {"domain", "application"},  # Infrastructure can use domain and application
    "api": {"application", "domain"},  # API can use application and domain
}

# Define forbidden import patterns (regex)
FORBIDDEN_PATTERNS: List[Dict[str, str]] = [
    {
        "pattern": r"from\s+(?:src\.)?infrastructure\.",
        "in_layer": "domain",
        "message": "Domain layer cannot import infrastructure layer",
    },
    {
        "pattern": r"import\s+(?:src\.)?infrastructure",
        "in_layer": "domain",
        "message": "Domain layer cannot import infrastructure layer",
    },
    {
        "pattern": r"from\s+(?:src\.)?api\.",
        "in_layer": "domain",
        "message": "Domain layer cannot import API layer",
    },
    {
        "pattern": r"from\s+(?:src\.)?infrastructure\.",
        "in_layer": "application",
        "message": "Application layer cannot import infrastructure layer",
    },
]

# Define source directory structure
# Update these paths to match your project
SOURCE_DIR = Path("src")
LAYER_PATHS: Dict[str, Path] = {
    "domain": SOURCE_DIR / "domain",
    "application": SOURCE_DIR / "application",
    "infrastructure": SOURCE_DIR / "infrastructure",
    "api": SOURCE_DIR / "api",
}

# ==============================================================================
# VALIDATION LOGIC (customize as needed)
# ==============================================================================


def check_forbidden_patterns() -> List[Dict[str, str]]:
    """Check for forbidden import patterns in each layer."""
    violations = []

    for forbidden in FORBIDDEN_PATTERNS:
        layer = forbidden["in_layer"]
        pattern = forbidden["pattern"]
        message = forbidden["message"]

        layer_path = LAYER_PATHS.get(layer)
        if not layer_path or not layer_path.exists():
            continue

        for file_path in layer_path.rglob("*.py"):
            if file_path.name == "__init__.py":
                continue

            content = file_path.read_text()
            matches = re.findall(pattern, content)

            if matches:
                violations.append(
                    {
                        "file": str(file_path.relative_to(Path.cwd())),
                        "layer": layer,
                        "violation": message,
                        "imports": matches,
                    }
                )

    return violations


def check_layer_dependencies() -> List[Dict[str, str]]:
    """Check that layers only import from allowed dependency layers."""
    violations = []

    for layer, allowed_deps in LAYER_DEPENDENCIES.items():
        layer_path = LAYER_PATHS.get(layer)
        if not layer_path or not layer_path.exists():
            continue

        for file_path in layer_path.rglob("*.py"):
            if file_path.name == "__init__.py":
                continue

            content = file_path.read_text()

            # Check imports from other layers
            for other_layer, other_path in LAYER_PATHS.items():
                if other_layer == layer:
                    continue

                if other_layer not in allowed_deps:
                    # Check for imports from forbidden layer
                    pattern = rf"from\s+(?:src\.)?{other_layer}\.|import\s+(?:src\.)?{other_layer}"
                    matches = re.findall(pattern, content)

                    if matches:
                        violations.append(
                            {
                                "file": str(file_path.relative_to(Path.cwd())),
                                "layer": layer,
                                "violation": f"{layer} layer cannot depend on {other_layer} layer",
                                "imports": matches,
                            }
                        )

    return violations


def check_circular_dependencies() -> List[Dict[str, str]]:
    """
    Check for circular dependencies between modules.

    This is a simplified check - customize for your needs.
    For production, consider using tools like:
    - pydeps (Python dependency graph)
    - import-linter (enforce import rules)
    """
    violations = []

    # Example: Check if module A imports module B and module B imports module A
    # Customize this logic for your project

    # This is a placeholder - implement based on your architecture
    # For now, we'll skip this check
    # TODO: Implement circular dependency detection if needed

    return violations


def print_violations(violations: List[Dict[str, str]]) -> None:
    """Print violations in a readable format."""
    if not violations:
        return

    print("\n❌ Architecture violations detected:\n")
    for i, v in enumerate(violations, 1):
        print(f"{i}. File: {v['file']}")
        print(f"   Layer: {v['layer']}")
        print(f"   Issue: {v['violation']}")
        if "imports" in v and v["imports"]:
            print(f"   Found: {', '.join(v['imports'][:3])}")
            if len(v["imports"]) > 3:
                print(f"   ... and {len(v['imports']) - 3} more")
        print()


def main() -> int:
    """Run architecture validation."""
    print("🔍 Running architecture validation...\n")

    # Check if source directory exists
    if not SOURCE_DIR.exists():
        print(f"ℹ️  Source directory not found: {SOURCE_DIR}")
        print("   Skipping architecture validation")
        return 0

    # Check if any layer paths exist
    existing_layers = {
        layer: path for layer, path in LAYER_PATHS.items() if path.exists()
    }

    if not existing_layers:
        print("ℹ️  No layer directories found")
        print("   Skipping architecture validation")
        return 0

    print(f"Checking layers: {', '.join(existing_layers.keys())}\n")

    # Run all validation checks
    all_violations = []

    # Check forbidden patterns
    forbidden_violations = check_forbidden_patterns()
    all_violations.extend(forbidden_violations)

    # Check layer dependencies
    dependency_violations = check_layer_dependencies()
    all_violations.extend(dependency_violations)

    # Check circular dependencies
    circular_violations = check_circular_dependencies()
    all_violations.extend(circular_violations)

    # Print results
    if all_violations:
        print_violations(all_violations)
        print(f"Total violations: {len(all_violations)}")
        print(
            "\nℹ️  Fix these violations or update validation rules in validate_architecture.py"
        )
        return 1
    else:
        print("✅ Architecture validation passed")
        print(f"   Checked {len(existing_layers)} layers")
        return 0


if __name__ == "__main__":
    sys.exit(main())
