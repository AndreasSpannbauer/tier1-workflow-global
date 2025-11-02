#!/usr/bin/env python3
"""
Enhanced Repository Map Generator with Scope Support

Generates focused repository maps based on predefined scopes for efficient
external review (ChatGPT, Gemini, etc).

Automatically generates both TXT and optimized PDF outputs in timestamped directories.

Usage:
    # Use predefined scope (creates both txt and pdf)
    python3 tools/repomap/generate_repomap.py --scope backend

    # List available scopes
    python3 tools/repomap/generate_repomap.py --list-scopes

    # Combine multiple scopes
    python3 tools/repomap/generate_repomap.py --scopes backend workflow

    # Custom patterns
    python3 tools/repomap/generate_repomap.py --include "src/**/*.py" --include "docs/**/*.md"

    # Output to specific location (disables automatic PDF generation)
    python3 tools/repomap/generate_repomap.py --scope review-ready --output /tmp/review.txt

    # Skip PDF generation
    python3 tools/repomap/generate_repomap.py --scope backend --no-pdf

    # Auto-detect project type and use appropriate scope
    python3 tools/repomap/generate_repomap.py --auto-detect
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from scope_manager import ScopeConfig, ProjectTypeDetector
from pdf_generator import convert_to_pdf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a scoped repository map for external review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Scope selection
    scope_group = parser.add_mutually_exclusive_group()
    scope_group.add_argument("--scope", help="Use a predefined scope (e.g., backend, workflow, review-ready)")
    scope_group.add_argument("--scopes", nargs="+", help="Combine multiple scopes")
    scope_group.add_argument("--list-scopes", action="store_true", help="List available scopes and exit")
    scope_group.add_argument(
        "--auto-detect", action="store_true", help="Auto-detect project type and use appropriate scope"
    )

    # Custom patterns
    parser.add_argument(
        "--include",
        action="append",
        dest="include_patterns",
        help="Additional glob patterns to include (can be repeated)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        dest="exclude_patterns",
        help="Additional glob patterns to exclude (can be repeated)",
    )

    # Output options
    parser.add_argument(
        "--output", type=Path, default=None, help="Output file path (default: repomaps/{timestamp}/repomap-{scope}.txt)"
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root (defaults to cwd)")
    parser.add_argument("--max-file-size", type=int, help="Override max file size (bytes)")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to scope configuration file (default: tools/repomap/repomap_scopes.json or tools/repomap_scopes.json)",
    )
    parser.add_argument("--no-pdf", action="store_true", help="Skip automatic PDF generation")

    # Statistics
    parser.add_argument("--stats", action="store_true", help="Show statistics about included files")

    return parser.parse_args()


def git_tracked_files(repo_root: Path) -> Iterable[str]:
    """Get list of git-tracked files."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print("Failed to list tracked files via git ls-files", file=sys.stderr)
        raise SystemExit(exc.returncode) from exc
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def should_include_file(
    path: Path, rel_path: str, include_patterns: list[str], exclude_patterns: list[str], max_file_size: int
) -> tuple[bool, str]:
    """
    Determine if file should be included.
    Returns (should_include, reason).
    """
    from scope_manager import matches_patterns

    if not path.is_file():
        return False, "not a file"

    # Check exclusions first
    if exclude_patterns and matches_patterns(rel_path, exclude_patterns):
        return False, "excluded by pattern"

    # Check inclusions
    if include_patterns and not matches_patterns(rel_path, include_patterns):
        return False, "not included by pattern"

    # Check file size
    if max_file_size and path.stat().st_size > max_file_size:
        return False, f"too large ({path.stat().st_size} bytes)"

    return True, "included"


def write_header(output: Path, repo_root: Path, file_count: int, scope_info: dict, total_size: int) -> None:
    """Write header with metadata."""
    timestamp = datetime.now(timezone.utc).isoformat()
    header_lines = [
        "# Scoped Repository Map",
        f"# Generated: {timestamp}",
        f"# Root: {repo_root}",
        f"# Scope: {scope_info.get('name', 'custom')}",
        f"# Description: {scope_info.get('description', 'Custom scope')}",
        f"# Files included: {file_count}",
        f"# Total size: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)",
        f"# Max file size: {scope_info.get('max_file_size', 'N/A')} bytes",
        "",
        "# Include patterns:",
    ]

    for pattern in scope_info.get("include_patterns", []):
        header_lines.append(f"#   - {pattern}")

    if scope_info.get("exclude_patterns"):
        header_lines.append("#")
        header_lines.append("# Exclude patterns:")
        for pattern in scope_info["exclude_patterns"]:
            header_lines.append(f"#   - {pattern}")

    header_lines.append("")
    header_lines.append("=" * 80)
    header_lines.append("")

    output.write_text("\n".join(header_lines), encoding="utf-8")


def append_file(output: Path, repo_root: Path, rel_path: str) -> int:
    """Append file content to output. Returns file size."""
    target = repo_root / rel_path
    try:
        content = target.read_text(encoding="utf-8")
        file_size = target.stat().st_size
    except UnicodeDecodeError:
        with output.open("a", encoding="utf-8") as handle:
            handle.write(f"--- File: {rel_path} (skipped: non-UTF-8) ---\n\n")
        return 0

    payload = [f"--- File: {rel_path} ({file_size:,} bytes) ---\n", content]
    if not content.endswith("\n"):
        payload.append("\n")
    payload.append("\n")

    with output.open("a", encoding="utf-8") as handle:
        handle.writelines(payload)

    return file_size


def find_config_path(repo_root: Path, config_arg: Path | None) -> Path:
    """
    Find the scope configuration file.
    Tries multiple locations in order of priority.
    """
    if config_arg:
        return config_arg

    # Try project-specific custom scopes first
    custom_config = repo_root / "tools" / "repomap_scopes_custom.json"
    if custom_config.exists():
        return custom_config

    # Try project-specific standard location
    project_config = repo_root / "tools" / "repomap_scopes.json"
    if project_config.exists():
        return project_config

    # Try tier1 global location
    global_config = repo_root / "tools" / "repomap" / "repomap_scopes.json"
    if global_config.exists():
        return global_config

    # Fallback to relative path from script location
    script_dir = Path(__file__).parent
    fallback_config = script_dir / "repomap_scopes.json"
    return fallback_config


def main() -> None:
    args = parse_args()
    repo_root = args.root.resolve()

    # Find and load scope configuration
    config_path = find_config_path(repo_root, args.config)
    scope_config = ScopeConfig(config_path)

    # Handle --list-scopes
    if args.list_scopes:
        scope_config.list_scopes()
        return

    # Determine scope to use
    if args.auto_detect:
        detector = ProjectTypeDetector(repo_root)
        project_type = detector.detect()
        print(f"Detected project type: {project_type}")

        # Select appropriate default scope based on project type
        if project_type == "backend":
            scope_name = "backend"
        elif project_type == "frontend":
            scope_name = "frontend"
        elif project_type == "fullstack":
            scope_name = "review-ready"
        else:
            scope_name = "workflow"

        print(f"Using scope: {scope_name}")
        scope_data = scope_config.get_scope(scope_name)
    elif args.scope:
        scope_data = scope_config.get_scope(args.scope)
        scope_name = args.scope
    elif args.scopes:
        # Merge multiple scopes
        scope_data = {
            "description": f"Combined: {', '.join(args.scopes)}",
            "include_patterns": [],
            "exclude_patterns": [],
            "max_file_size": 200000,
        }
        for scope_name in args.scopes:
            scope = scope_config.get_scope(scope_name)
            scope_data["include_patterns"].extend(scope.get("include_patterns", []))
            scope_data["exclude_patterns"].extend(scope.get("exclude_patterns", []))
        scope_name = "+".join(args.scopes)
    elif args.include_patterns:
        # Custom patterns
        scope_data = {
            "description": "Custom patterns",
            "include_patterns": args.include_patterns,
            "exclude_patterns": args.exclude_patterns or [],
            "max_file_size": args.max_file_size or 200000,
        }
        scope_name = "custom"
    else:
        print("Error: Must specify --scope, --scopes, --auto-detect, --include, or --list-scopes", file=sys.stderr)
        sys.exit(1)

    # Add custom patterns if provided
    if args.include_patterns:
        scope_data["include_patterns"].extend(args.include_patterns)
    if args.exclude_patterns:
        scope_data["exclude_patterns"].extend(args.exclude_patterns)

    # Override max file size if provided
    if args.max_file_size:
        scope_data["max_file_size"] = args.max_file_size

    # Determine output path with timestamped directory structure
    custom_output = args.output is not None
    if custom_output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Create timestamped directory structure: repomaps/YYYYMMDD_HHMMSS/
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = repo_root / "repomaps" / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        output = output_dir / f"repomap-{scope_name}.txt"

    # Get tracked files
    tracked = git_tracked_files(repo_root)

    # Filter files based on scope
    included_files = []
    excluded_stats = {}

    for rel_path in tracked:
        full_path = repo_root / rel_path
        should_include, reason = should_include_file(
            full_path,
            rel_path,
            scope_data.get("include_patterns", []),
            scope_data.get("exclude_patterns", []),
            scope_data.get("max_file_size", 200000),
        )

        if should_include:
            included_files.append(rel_path)
        else:
            excluded_stats[reason] = excluded_stats.get(reason, 0) + 1

    # Write header
    scope_info = {
        "name": scope_name,
        "description": scope_data.get("description", ""),
        "include_patterns": scope_data.get("include_patterns", []),
        "exclude_patterns": scope_data.get("exclude_patterns", []),
        "max_file_size": scope_data.get("max_file_size", 200000),
    }

    total_size = 0
    write_header(output, repo_root, len(included_files), scope_info, 0)  # Will update later

    # Append files
    for rel_path in sorted(included_files):
        file_size = append_file(output, repo_root, rel_path)
        total_size += file_size

    # Update header with final size
    content = output.read_text()
    updated_content = content.replace(
        "# Total size: 0 bytes (0.00 MB)", f"# Total size: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)"
    )
    output.write_text(updated_content)

    # Print summary
    print(f"✅ Scoped repository map generated: {output}")
    print(f"📊 Files included: {len(included_files)}")
    print(f"📏 Total size: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")

    if args.stats or excluded_stats:
        print("\n📉 Excluded files:")
        for reason, count in sorted(excluded_stats.items()):
            print(f"  - {reason}: {count} files")

    # Automatically generate PDF (unless disabled or custom output specified)
    if not args.no_pdf and not custom_output:
        print("\n📄 Generating optimized PDF...")
        pdf_file = output.parent / f"{output.stem}.pdf"
        success = convert_to_pdf(output, pdf_file)

        if success:
            txt_size_mb = output.stat().st_size / (1024 * 1024)
            pdf_size_mb = pdf_file.stat().st_size / (1024 * 1024)
            compression_ratio = (1 - pdf_size_mb / txt_size_mb) * 100
            print(f"📦 Compression: {compression_ratio:.1f}% reduction ({txt_size_mb:.2f} MB → {pdf_size_mb:.2f} MB)")
        else:
            print("⚠️  PDF generation failed, but txt file is available")

    print(f"\n📂 Output directory: {output.parent if not custom_output else output.parent}")


if __name__ == "__main__":
    main()
