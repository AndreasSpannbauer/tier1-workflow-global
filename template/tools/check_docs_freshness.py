#!/usr/bin/env python3
"""
Documentation Freshness Check Script

MIT License - Copyright (c) 2025

Tracks whether documentation is up-to-date with code changes by comparing
modification timestamps. Configurable mapping rules determine which docs
should be updated when specific code files change.

Example configuration (.freshness-check.json):
{
    "mappings": [
        {
            "code_patterns": ["src/**/*.py"],
            "doc_patterns": ["docs/api/*.md"],
            "threshold_days": 7,
            "severity": "warning"
        },
        {
            "code_patterns": ["src/core/*.py", "src/main.py"],
            "doc_patterns": ["README.md", "docs/getting-started.md"],
            "threshold_days": 3,
            "severity": "error"
        }
    ],
    "ignore_patterns": [
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/vendor/**",
        "**/*.pyc",
        ".git/**"
    ],
    "use_git_timestamps": true
}

Usage:
    python check_docs_freshness.py
    python check_docs_freshness.py --json
    python check_docs_freshness.py --threshold-days 14 --verbose
    python check_docs_freshness.py --config custom-config.json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Literal
import subprocess


@dataclass
class MappingRule:
    """Defines which docs should be updated when code changes."""
    code_patterns: List[str]
    doc_patterns: List[str]
    threshold_days: int = 7
    severity: Literal["warning", "error"] = "warning"


@dataclass
class FreshnessConfig:
    """Configuration for documentation freshness checks."""
    mappings: List[MappingRule] = field(default_factory=list)
    ignore_patterns: List[str] = field(default_factory=list)
    use_git_timestamps: bool = True

    @classmethod
    def from_dict(cls, data: Dict) -> "FreshnessConfig":
        """Load configuration from dictionary."""
        mappings = [
            MappingRule(**mapping)
            for mapping in data.get("mappings", [])
        ]
        return cls(
            mappings=mappings,
            ignore_patterns=data.get("ignore_patterns", []),
            use_git_timestamps=data.get("use_git_timestamps", True)
        )

    @classmethod
    def load(cls, config_path: Path) -> "FreshnessConfig":
        """Load configuration from JSON file."""
        if not config_path.exists():
            return cls.default()

        with open(config_path) as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def default(cls) -> "FreshnessConfig":
        """Default configuration for Python projects."""
        return cls(
            mappings=[
                MappingRule(
                    code_patterns=["src/**/*.py", "*.py"],
                    doc_patterns=["docs/**/*.md", "README.md"],
                    threshold_days=7,
                    severity="warning"
                )
            ],
            ignore_patterns=[
                "**/node_modules/**",
                "**/__pycache__/**",
                "**/vendor/**",
                "**/*.pyc",
                ".git/**",
                "**/.pytest_cache/**",
                "**/__generated__/**"
            ]
        )


@dataclass
class StaleDoc:
    """Represents stale documentation that needs updating."""
    doc_path: Path
    newest_code_file: Path
    code_modified: datetime
    doc_modified: datetime
    staleness_days: int
    severity: Literal["warning", "error"]
    rule: MappingRule


@dataclass
class FreshnessReport:
    """Report of documentation freshness check."""
    stale_docs: List[StaleDoc] = field(default_factory=list)
    total_mappings_checked: int = 0
    total_code_files: int = 0
    total_doc_files: int = 0
    check_timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_errors(self) -> bool:
        """Check if any stale docs are marked as errors."""
        return any(doc.severity == "error" for doc in self.stale_docs)

    @property
    def has_warnings(self) -> bool:
        """Check if any stale docs are marked as warnings."""
        return any(doc.severity == "warning" for doc in self.stale_docs)

    @property
    def is_fresh(self) -> bool:
        """Check if all documentation is fresh."""
        return len(self.stale_docs) == 0

    def to_dict(self) -> Dict:
        """Convert report to dictionary for JSON output."""
        return {
            "check_timestamp": self.check_timestamp.isoformat(),
            "is_fresh": self.is_fresh,
            "has_warnings": self.has_warnings,
            "has_errors": self.has_errors,
            "total_mappings_checked": self.total_mappings_checked,
            "total_code_files": self.total_code_files,
            "total_doc_files": self.total_doc_files,
            "stale_docs": [
                {
                    "doc_path": str(doc.doc_path),
                    "newest_code_file": str(doc.newest_code_file),
                    "code_modified": doc.code_modified.isoformat(),
                    "doc_modified": doc.doc_modified.isoformat(),
                    "staleness_days": doc.staleness_days,
                    "severity": doc.severity,
                    "suggested_action": f"Update {doc.doc_path} (code changed {doc.staleness_days} days ago)"
                }
                for doc in self.stale_docs
            ]
        }


class FreshnessChecker:
    """Check documentation freshness against code changes."""

    def __init__(self, config: FreshnessConfig, root_dir: Path, verbose: bool = False):
        self.config = config
        self.root_dir = root_dir
        self.verbose = verbose
        self._git_available = self._check_git()

    def _check_git(self) -> bool:
        """Check if git is available and repo exists."""
        if not self.config.use_git_timestamps:
            return False

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.root_dir,
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_file_timestamp(self, file_path: Path) -> Optional[datetime]:
        """Get file modification timestamp (from git or filesystem)."""
        if self._git_available:
            try:
                # Get last commit time for this file
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%ct", "--", str(file_path)],
                    cwd=self.root_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                timestamp = result.stdout.strip()
                if timestamp:
                    return datetime.fromtimestamp(int(timestamp))
            except subprocess.CalledProcessError:
                pass

        # Fallback to filesystem mtime
        if file_path.exists():
            return datetime.fromtimestamp(file_path.stat().st_mtime)
        return None

    def _match_patterns(self, patterns: List[str]) -> List[Path]:
        """Find all files matching glob patterns."""
        matched_files = set()

        for pattern in patterns:
            for file_path in self.root_dir.glob(pattern):
                if not file_path.is_file():
                    continue

                # Check if file matches ignore patterns
                relative_path = file_path.relative_to(self.root_dir)
                if any(relative_path.match(ignore) for ignore in self.config.ignore_patterns):
                    continue

                matched_files.add(file_path)

        return sorted(matched_files)

    def _check_mapping_rule(self, rule: MappingRule) -> List[StaleDoc]:
        """Check a single mapping rule for stale documentation."""
        stale_docs = []

        # Find all code and doc files for this rule
        code_files = self._match_patterns(rule.code_patterns)
        doc_files = self._match_patterns(rule.doc_patterns)

        if not code_files or not doc_files:
            if self.verbose:
                print(f"  Skipping rule: no code files ({len(code_files)}) or doc files ({len(doc_files)})")
            return []

        # Find newest code file
        code_timestamps = {
            f: self._get_file_timestamp(f)
            for f in code_files
        }
        code_timestamps = {f: ts for f, ts in code_timestamps.items() if ts}

        if not code_timestamps:
            return []

        newest_code_file = max(code_timestamps, key=code_timestamps.get)
        newest_code_time = code_timestamps[newest_code_file]

        # Check each doc file
        for doc_file in doc_files:
            doc_time = self._get_file_timestamp(doc_file)
            if not doc_time:
                continue

            # Calculate staleness
            time_diff = newest_code_time - doc_time
            staleness_days = time_diff.days

            if staleness_days > rule.threshold_days:
                stale_docs.append(StaleDoc(
                    doc_path=doc_file.relative_to(self.root_dir),
                    newest_code_file=newest_code_file.relative_to(self.root_dir),
                    code_modified=newest_code_time,
                    doc_modified=doc_time,
                    staleness_days=staleness_days,
                    severity=rule.severity,
                    rule=rule
                ))

        return stale_docs

    def check(self) -> FreshnessReport:
        """Run freshness check across all mapping rules."""
        report = FreshnessReport()
        all_code_files = set()
        all_doc_files = set()

        if self.verbose:
            print(f"Checking documentation freshness in {self.root_dir}")
            print(f"Using git timestamps: {self._git_available}")
            print()

        for i, rule in enumerate(self.config.mappings, 1):
            if self.verbose:
                print(f"Rule {i}/{len(self.config.mappings)}:")
                print(f"  Code: {rule.code_patterns}")
                print(f"  Docs: {rule.doc_patterns}")
                print(f"  Threshold: {rule.threshold_days} days ({rule.severity})")

            stale_docs = self._check_mapping_rule(rule)
            report.stale_docs.extend(stale_docs)

            # Track file counts
            code_files = self._match_patterns(rule.code_patterns)
            doc_files = self._match_patterns(rule.doc_patterns)
            all_code_files.update(code_files)
            all_doc_files.update(doc_files)

            if self.verbose:
                print(f"  Found: {len(code_files)} code files, {len(doc_files)} doc files")
                print(f"  Stale: {len(stale_docs)} doc(s)")
                print()

        report.total_mappings_checked = len(self.config.mappings)
        report.total_code_files = len(all_code_files)
        report.total_doc_files = len(all_doc_files)

        return report


def print_report(report: FreshnessReport, verbose: bool = False):
    """Print human-readable freshness report."""
    try:
        from colorama import Fore, Style, init
        init(autoreset=True)
        has_color = True
    except ImportError:
        # Fallback without colors
        class DummyColor:
            def __getattr__(self, name):
                return ""
        Fore = Style = DummyColor()
        has_color = False

    print(f"\n{'='*70}")
    print(f"Documentation Freshness Report")
    print(f"{'='*70}\n")

    print(f"Checked: {report.total_mappings_checked} mapping rule(s)")
    print(f"Files: {report.total_code_files} code, {report.total_doc_files} docs")
    print(f"Timestamp: {report.check_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

    if report.is_fresh:
        print(f"{Fore.GREEN}✓ All documentation is up-to-date!{Style.RESET_ALL}\n")
        return

    # Group by severity
    errors = [d for d in report.stale_docs if d.severity == "error"]
    warnings = [d for d in report.stale_docs if d.severity == "warning"]

    if errors:
        print(f"{Fore.RED}ERRORS ({len(errors)}):{Style.RESET_ALL}")
        for doc in sorted(errors, key=lambda d: d.staleness_days, reverse=True):
            print(f"  {Fore.RED}✗{Style.RESET_ALL} {doc.doc_path}")
            print(f"    Code changed: {doc.code_modified.strftime('%Y-%m-%d')} ({doc.newest_code_file})")
            print(f"    Doc modified: {doc.doc_modified.strftime('%Y-%m-%d')}")
            print(f"    Staleness: {Fore.RED}{doc.staleness_days} days{Style.RESET_ALL} (threshold: {doc.rule.threshold_days})")
            print()

    if warnings:
        print(f"{Fore.YELLOW}WARNINGS ({len(warnings)}):{Style.RESET_ALL}")
        for doc in sorted(warnings, key=lambda d: d.staleness_days, reverse=True):
            print(f"  {Fore.YELLOW}⚠{Style.RESET_ALL} {doc.doc_path}")
            print(f"    Code changed: {doc.code_modified.strftime('%Y-%m-%d')} ({doc.newest_code_file})")
            print(f"    Doc modified: {doc.doc_modified.strftime('%Y-%m-%d')}")
            print(f"    Staleness: {Fore.YELLOW}{doc.staleness_days} days{Style.RESET_ALL} (threshold: {doc.rule.threshold_days})")
            print()

    print(f"{'='*70}")
    print(f"Summary: {Fore.RED}{len(errors)} error(s){Style.RESET_ALL}, {Fore.YELLOW}{len(warnings)} warning(s){Style.RESET_ALL}")
    print(f"{'='*70}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check if documentation is up-to-date with code changes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(".freshness-check.json"),
        help="Path to configuration file (default: .freshness-check.json)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report as JSON"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--threshold-days",
        type=int,
        help="Override threshold days for all mappings"
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=Path.cwd(),
        help="Root directory to check (default: current directory)"
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate default configuration file and exit"
    )

    args = parser.parse_args()

    # Generate config mode
    if args.generate_config:
        config_path = args.config
        if config_path.exists():
            print(f"Error: {config_path} already exists", file=sys.stderr)
            return 1

        default_config = FreshnessConfig.default()
        config_dict = {
            "mappings": [
                {
                    "code_patterns": rule.code_patterns,
                    "doc_patterns": rule.doc_patterns,
                    "threshold_days": rule.threshold_days,
                    "severity": rule.severity
                }
                for rule in default_config.mappings
            ],
            "ignore_patterns": default_config.ignore_patterns,
            "use_git_timestamps": default_config.use_git_timestamps
        }

        with open(config_path, "w") as f:
            json.dump(config_dict, f, indent=2)

        print(f"Generated default configuration: {config_path}")
        return 0

    # Load configuration
    config = FreshnessConfig.load(args.config)

    # Override threshold if specified
    if args.threshold_days is not None:
        for mapping in config.mappings:
            mapping.threshold_days = args.threshold_days

    # Run check
    checker = FreshnessChecker(config, args.root_dir, verbose=args.verbose)
    report = checker.check()

    # Output report
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print_report(report, verbose=args.verbose)

    # Exit code
    if report.has_errors:
        return 1
    elif report.has_warnings:
        return 0  # Warnings don't fail CI
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
