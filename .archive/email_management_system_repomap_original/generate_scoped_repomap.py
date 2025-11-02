#!/usr/bin/env python3
"""
Enhanced Repository Map Generator with Scope Support

Generates focused repository maps based on predefined scopes for efficient
external review (ChatGPT, Gemini, etc).

Automatically generates both TXT and optimized PDF outputs in timestamped directories.

EXPERIMENTAL: Optional Repomix integration for tree-sitter compression (--engine repomix).
Falls back to proven glob-based implementation if Repomix unavailable.

Usage:
    # Use predefined scope (creates both txt and pdf)
    python3 tools/generate_scoped_repomap.py --scope backend

    # List available scopes
    python3 tools/generate_scoped_repomap.py --list-scopes

    # Combine multiple scopes
    python3 tools/generate_scoped_repomap.py --scopes backend workflow

    # Custom patterns
    python3 tools/generate_scoped_repomap.py --include "src/**/*.py" --include "docs/**/*.md"

    # Output to specific location (disables automatic PDF generation)
    python3 tools/generate_scoped_repomap.py --scope review-ready --output /tmp/review.txt

    # Skip PDF generation
    python3 tools/generate_scoped_repomap.py --scope backend --no-pdf

    # Engine selection (EXPERIMENTAL)
    python3 tools/generate_scoped_repomap.py --scope backend --engine auto      # Try Repomix, fallback to proven
    python3 tools/generate_scoped_repomap.py --scope backend --engine repomix   # Force Repomix (fails if unavailable)
    python3 tools/generate_scoped_repomap.py --scope backend --engine proven    # Force proven implementation
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# Import Repomix adapter
try:
    from repomix_adapter import RepomixAdapter, RepomixError, RepomixNotAvailableError, RepomixFailedError
    REPOMIX_AVAILABLE = True
except ImportError:
    REPOMIX_AVAILABLE = False


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
        "--config", type=Path, default=Path("tools/repomap_scopes.json"), help="Path to scope configuration file"
    )
    parser.add_argument("--no-pdf", action="store_true", help="Skip automatic PDF generation")

    # Engine selection (EXPERIMENTAL)
    parser.add_argument(
        "--engine",
        choices=["auto", "proven", "repomix"],
        default="proven",
        help=(
            "Repomap generation engine (default: proven). "
            "auto=try Repomix, fallback to proven; "
            "proven=glob-based (always works); "
            "repomix=force Repomix (EXPERIMENTAL, fails if unavailable)"
        ),
    )

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


def matches_patterns(path: str, patterns: list[str]) -> bool:
    """Check if path matches any of the glob patterns."""
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False


def should_include_file(
    path: Path, rel_path: str, include_patterns: list[str], exclude_patterns: list[str], max_file_size: int
) -> tuple[bool, str]:
    """
    Determine if file should be included.
    Returns (should_include, reason).
    """
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


def convert_to_pdf(txt_file: Path, pdf_file: Path) -> bool:
    """
    Convert text file to optimized PDF using enscript and ps2pdf.
    Returns True on success, False on failure.
    """
    try:
        # Step 1: Convert to PostScript with enscript (small font, no header)
        ps_file = txt_file.parent / f"{txt_file.stem}.ps"

        print(f"🔄 Converting to PostScript...")
        enscript_result = subprocess.run(
            [
                "enscript",
                "-B",  # No header
                "-f", "Courier4",  # 4pt font for compact output
                "--word-wrap",  # Wrap long lines
                "--media=A4",  # A4 paper size
                "-o", str(ps_file),
                str(txt_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if enscript_result.returncode != 0:
            print(f"⚠️  enscript warning (continuing): {enscript_result.stderr[:200]}")

        if not ps_file.exists():
            print("❌ PostScript file not created")
            return False

        # Step 2: Convert PostScript to compressed PDF
        print(f"🔄 Converting to compressed PDF...")
        ps2pdf_result = subprocess.run(
            [
                "ps2pdf",
                "-dPDFSETTINGS=/ebook",  # Optimize for small file size
                "-dCompressPages=true",
                "-dUseFlateCompression=true",
                str(ps_file),
                str(pdf_file),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Clean up PostScript file
        ps_file.unlink()

        if not pdf_file.exists():
            print("❌ PDF file not created")
            return False

        # Check size
        pdf_size_mb = pdf_file.stat().st_size / (1024 * 1024)
        print(f"✅ PDF created: {pdf_file.name} ({pdf_size_mb:.2f} MB)")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ PDF conversion failed: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Required tool not found: {e}")
        print("   Install with: sudo apt-get install enscript ghostscript")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during PDF conversion: {e}")
        return False


def generate_with_proven_engine(
    scope_name: str,
    scope_data: dict,
    output: Path,
    repo_root: Path,
    args: argparse.Namespace,
) -> tuple[int, int]:
    """
    Generate repomap using proven glob-based implementation.

    Returns:
        Tuple of (file_count, total_size)
    """
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

    # Print stats
    if args.stats or excluded_stats:
        print("\n📉 Excluded files:")
        for reason, count in sorted(excluded_stats.items()):
            print(f"  - {reason}: {count} files")

    return len(included_files), total_size


def main() -> None:
    args = parse_args()
    repo_root = args.root.resolve()

    # Load scope configuration
    config_path = repo_root / args.config
    scope_config = ScopeConfig(config_path)

    # Handle --list-scopes
    if args.list_scopes:
        scope_config.list_scopes()
        return

    # Determine scope to use
    if args.scope:
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
        print("Error: Must specify --scope, --scopes, --include, or --list-scopes", file=sys.stderr)
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

    # Engine selection with fallback logic
    engine_used = "proven"  # Default
    file_count = 0
    total_size = 0

    if args.engine == "repomix":
        # Force Repomix - fail if unavailable
        if not REPOMIX_AVAILABLE:
            print("❌ Repomix adapter not available (import failed)", file=sys.stderr)
            print("Install Repomix: npm install -g repomix", file=sys.stderr)
            sys.exit(1)

        adapter = RepomixAdapter()
        if not adapter.is_available():
            print("❌ Repomix not available (npx repomix failed)", file=sys.stderr)
            print("Install Repomix: npm install -g repomix", file=sys.stderr)
            sys.exit(1)

        try:
            print(f"🔧 Using Repomix engine...")
            _, stats = adapter.generate_with_repomix(scope_name, scope_data, output, repo_root)
            file_count = stats.file_count
            total_size = stats.output_size_bytes
            engine_used = "repomix"
        except RepomixError as e:
            print(f"❌ Repomix generation failed: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.engine == "auto":
        # Try Repomix, fallback to proven
        if REPOMIX_AVAILABLE:
            adapter = RepomixAdapter()
            if adapter.is_available():
                try:
                    print(f"🔧 Trying Repomix engine...")
                    _, stats = adapter.generate_with_repomix(scope_name, scope_data, output, repo_root)
                    file_count = stats.file_count
                    total_size = stats.output_size_bytes
                    engine_used = "repomix"
                except RepomixError as e:
                    print(f"⚠️  Repomix failed: {e}")
                    print(f"🔄 Falling back to proven engine...")
                    file_count, total_size = generate_with_proven_engine(scope_name, scope_data, output, repo_root, args)
                    engine_used = "proven (fallback)"
            else:
                print(f"⚠️  Repomix not available, using proven engine")
                file_count, total_size = generate_with_proven_engine(scope_name, scope_data, output, repo_root, args)
                engine_used = "proven (fallback)"
        else:
            print(f"⚠️  Repomix adapter not available, using proven engine")
            file_count, total_size = generate_with_proven_engine(scope_name, scope_data, output, repo_root, args)
            engine_used = "proven (fallback)"

    else:  # args.engine == "proven"
        # Use proven implementation
        print(f"🔧 Using proven glob-based engine...")
        file_count, total_size = generate_with_proven_engine(scope_name, scope_data, output, repo_root, args)
        engine_used = "proven"

    # Print summary
    print(f"\n✅ Scoped repository map generated: {output}")
    print(f"🔧 Engine: {engine_used}")
    print(f"📊 Files included: {file_count}")
    print(f"📏 Total size: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")

    # Show token stats if using Repomix
    if "repomix" in engine_used.lower() and args.engine in ("repomix", "auto"):
        # Try to get stats from the adapter if available
        if REPOMIX_AVAILABLE and 'stats' in locals():
            if stats.total_tokens > 0:
                print(f"🎯 Estimated tokens: {stats.total_tokens:,}")
                print(f"📝 Total characters: {stats.total_chars:,}")
                if stats.total_chars > 0:
                    print(f"📐 Chars per token: {stats.total_chars / stats.total_tokens:.2f}")

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
