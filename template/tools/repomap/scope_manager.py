#!/usr/bin/env python3
"""
Scope Management Module

Manages scope configurations from JSON file and provides project type detection.
"""

from __future__ import annotations

import fnmatch
import json
import sys
from pathlib import Path


class ScopeConfig:
    """Manages scope configurations from JSON file."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load scope configuration from JSON."""
        if not self.config_path.exists():
            print(f"Warning: Config file not found: {self.config_path}", file=sys.stderr)
            return {"scopes": {}, "scope_combinations": {}}

        try:
            return json.loads(self.config_path.read_text())
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}", file=sys.stderr)
            sys.exit(1)

    def list_scopes(self) -> None:
        """Display available scopes."""
        print("Available Scopes:")
        print("=" * 80)

        for name, scope in self.config.get("scopes", {}).items():
            print(f"\n{name}:")
            print(f"  Description: {scope.get('description', 'N/A')}")
            print(f"  Include patterns: {len(scope.get('include_patterns', []))}")
            print(f"  Max file size: {scope.get('max_file_size', 'N/A')} bytes")

        combinations = self.config.get("scope_combinations", {})
        if combinations:
            print("\n\nScope Combinations:")
            print("=" * 80)
            for name, combo in combinations.items():
                print(f"\n{name}:")
                print(f"  Description: {combo.get('description', 'N/A')}")
                print(f"  Includes scopes: {', '.join(combo.get('scopes', []))}")
                print(f"  Max total size: {combo.get('max_total_size', 'N/A')} bytes")

    def get_scope(self, scope_name: str) -> dict:
        """Get a specific scope configuration."""
        if scope_name in self.config.get("scopes", {}):
            return self.config["scopes"][scope_name]

        # Check if it's a combination
        if scope_name in self.config.get("scope_combinations", {}):
            combo = self.config["scope_combinations"][scope_name]
            # Merge all scopes in the combination
            merged = {
                "description": combo.get("description", ""),
                "include_patterns": [],
                "exclude_patterns": [],
                "max_file_size": combo.get("max_total_size", 200000),
            }

            for scope in combo.get("scopes", []):
                if scope in self.config.get("scopes", {}):
                    scope_data = self.config["scopes"][scope]
                    merged["include_patterns"].extend(scope_data.get("include_patterns", []))
                    merged["exclude_patterns"].extend(scope_data.get("exclude_patterns", []))

            return merged

        print(f"Error: Scope '{scope_name}' not found", file=sys.stderr)
        print("Run with --list-scopes to see available scopes", file=sys.stderr)
        sys.exit(1)


class ProjectTypeDetector:
    """Detects project type based on file patterns."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def detect(self) -> str:
        """
        Detect project type based on file patterns.
        Returns: backend, frontend, fullstack, or workflow
        """
        has_backend = self._has_backend_files()
        has_frontend = self._has_frontend_files()
        has_workflow = self._has_workflow_files()

        if has_backend and has_frontend:
            return "fullstack"
        elif has_backend:
            return "backend"
        elif has_frontend:
            return "frontend"
        elif has_workflow:
            return "workflow"
        else:
            return "generic"

    def _has_backend_files(self) -> bool:
        """Check if project has backend files."""
        backend_indicators = [
            "src/**/*.py",
            "api/**/*.py",
            "server/**/*.go",
            "api/**/*.ts",
            "requirements.txt",
            "pyproject.toml",
            "go.mod",
        ]

        for pattern in backend_indicators:
            if self._find_files(pattern):
                return True
        return False

    def _has_frontend_files(self) -> bool:
        """Check if project has frontend files."""
        frontend_indicators = [
            "frontend/**/*.tsx",
            "frontend/**/*.jsx",
            "src/**/*.tsx",
            "src/**/*.jsx",
            "components/**/*.tsx",
            "components/**/*.jsx",
            "app/**/*.tsx",
            "pages/**/*.tsx",
        ]

        for pattern in frontend_indicators:
            if self._find_files(pattern):
                return True
        return False

    def _has_workflow_files(self) -> bool:
        """Check if project has workflow files."""
        workflow_indicators = [
            ".tasks/**/*.md",
            ".claude/**/*.md",
            "CLAUDE.md",
        ]

        for pattern in workflow_indicators:
            if self._find_files(pattern):
                return True
        return False

    def _find_files(self, pattern: str) -> list[Path]:
        """Find files matching pattern."""
        parts = pattern.split("/")

        # Handle ** recursive patterns
        if "**" in parts:
            idx = parts.index("**")
            base_dir = self.repo_root / "/".join(parts[:idx]) if idx > 0 else self.repo_root
            file_pattern = "/".join(parts[idx + 1 :])

            if not base_dir.exists():
                return []

            matches = []
            for path in base_dir.rglob(file_pattern):
                if path.is_file():
                    matches.append(path)
                    if len(matches) >= 5:  # Early exit for performance
                        break
            return matches
        else:
            # Simple glob pattern
            matches = list(self.repo_root.glob(pattern))
            return [p for p in matches if p.is_file()][:5]


def matches_patterns(path: str, patterns: list[str]) -> bool:
    """Check if path matches any of the glob patterns."""
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False
