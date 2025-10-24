#!/usr/bin/env python3
"""
SCALAR Path Replacement Script

Fixes 312 hardcoded absolute paths identified in Stage 1 analysis.
Uses 4 replacement strategies:
1. Remove redundant sys.path.append() calls
2. Convert to relative imports
3. Extract to environment variables
4. Context-aware replacements

DRY RUN by default - use --execute to apply changes.
"""

import argparse
import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

SCALAR_ROOT = Path.home() / "SCALAR"

# Files requiring path updates (from Stage 1 analysis)
FILES_TO_UPDATE = [
    # High priority (core modules)
    "modules/collection_utils/complete_validation_pipeline.py",
    "modules/collection_utils/fast_complete_pipeline.py",
    "modules/collection_utils/scalar_reference_workflow.py",
    "modules/collection_utils/extract_gemini_batch.py",
    "modules/collection_utils/production_reference_workflow.py",
    "modules/analysis_utils/pipeline.py",

    # Medium priority (test/validation scripts)
    "modules/bulk_processing/test_unified_parser.py",
    "scripts/quick_biolord_deployment.py",
    "validation_frameworks/comprehensive_validation_cli.py",

    # Configuration files
    "config/config.yaml",
    "config/gpu_services/gpu_config.py",
]

# Path patterns to find and replace
PATH_PATTERNS = {
    # Old second_brain paths
    "second_brain_root": r"/home/andreas-spannbauer/coding_projects/projects/01_second_brain/SCALAR_workflow",
    "obsidian_vault": r"/home/andreas-spannbauer/coding_projects/projects/01_second_brain/obsidian_llm_vault",

    # GPU server IP (Tailscale)
    "gpu_server_tailscale": r"100\.102\.171\.107",

    # GPU server IP (Direct LAN - preferred)
    "gpu_server_lan": r"192\.168\.10\.10",

    # Model cache paths
    "model_cache": r"/home/andreas-spannbauer/coding_projects/projects/01_second_brain/SCALAR_workflow/models",

    # Data directories
    "data_dir": r"/home/andreas-spannbauer/coding_projects/projects/01_second_brain/SCALAR_workflow/data",
}

# Replacement templates
REPLACEMENTS = {
    # Use environment variables for paths
    "scalar_root": 'os.environ.get("SCALAR_ROOT", str(Path.home() / "SCALAR"))',
    "obsidian_vault": 'os.environ.get("OBSIDIAN_VAULT_PATH", str(Path.home() / "coding_projects/projects/01_second_brain/obsidian_llm_vault"))',

    # GPU server - use environment variable
    "gpu_server": 'os.environ.get("GPU_SERVER_HOST", "192.168.10.10")',

    # Model cache - relative to SCALAR_ROOT
    "model_cache": 'str(Path(os.environ.get("SCALAR_ROOT", str(Path.home() / "SCALAR"))) / "models")',

    # Data directory - relative to SCALAR_ROOT
    "data_dir": 'str(Path(os.environ.get("SCALAR_ROOT", str(Path.home() / "SCALAR"))) / "data")',
}

# sys.path.append() calls to remove (redundant with proper package installation)
SYS_PATH_PATTERNS = [
    r'sys\.path\.append\([^)]+\)',
    r'sys\.path\.insert\([^)]+\)',
]

# ============================================================================
# STRATEGY 1: Remove sys.path.append() Calls
# ============================================================================

def remove_sys_path_calls(content: str, dry_run: bool = True) -> Tuple[str, List[str]]:
    """Remove redundant sys.path.append() and sys.path.insert() calls."""
    changes = []

    for pattern in SYS_PATH_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            for match in matches:
                changes.append(f"REMOVE: {match}")
                if not dry_run:
                    # Comment out instead of deleting (safer)
                    content = content.replace(match, f"# REMOVED: {match}")

    return content, changes

# ============================================================================
# STRATEGY 2: Convert to Relative Imports
# ============================================================================

def convert_to_relative_imports(content: str, file_path: Path, dry_run: bool = True) -> Tuple[str, List[str]]:
    """Convert absolute imports to relative imports where possible."""
    changes = []

    # Pattern: from modules.xxx import yyy
    # Should be: from .xxx import yyy (if in modules/)
    # or: from ..xxx import yyy (if in modules/submodule/)

    if "modules/" in str(file_path):
        # Determine relative depth
        parts = file_path.relative_to(SCALAR_ROOT).parts
        if parts[0] == "modules":
            depth = len(parts) - 2  # -2 for "modules" and filename

            # Find absolute imports
            import_pattern = r'from modules\.(\w+)'
            matches = re.findall(import_pattern, content)

            for match in matches:
                old_import = f"from modules.{match}"
                new_import = f"from {'.' * (depth + 1)}{match}" if depth >= 0 else f"from .{match}"

                if old_import in content:
                    changes.append(f"RELATIVE: {old_import} → {new_import}")
                    if not dry_run:
                        content = content.replace(old_import, new_import)

    return content, changes

# ============================================================================
# STRATEGY 3: Extract to Environment Variables
# ============================================================================

def extract_to_env_vars(content: str, dry_run: bool = True) -> Tuple[str, List[str]]:
    """Replace hardcoded paths with environment variable lookups."""
    changes = []

    replacements_made = []

    # Replace second_brain root paths
    pattern = PATH_PATTERNS["second_brain_root"]
    if re.search(pattern, content):
        changes.append(f"ENV_VAR: {pattern} → SCALAR_ROOT")
        if not dry_run:
            content = re.sub(pattern, REPLACEMENTS["scalar_root"], content)
        replacements_made.append("SCALAR_ROOT")

    # Replace Obsidian vault paths
    pattern = PATH_PATTERNS["obsidian_vault"]
    if re.search(pattern, content):
        changes.append(f"ENV_VAR: {pattern} → OBSIDIAN_VAULT_PATH")
        if not dry_run:
            content = re.sub(pattern, REPLACEMENTS["obsidian_vault"], content)
        replacements_made.append("OBSIDIAN_VAULT_PATH")

    # Replace GPU server IPs
    for gpu_key in ["gpu_server_tailscale", "gpu_server_lan"]:
        pattern = PATH_PATTERNS[gpu_key]
        if re.search(pattern, content):
            changes.append(f"ENV_VAR: {pattern} → GPU_SERVER_HOST")
            if not dry_run:
                content = re.sub(pattern, REPLACEMENTS["gpu_server"], content)
            replacements_made.append("GPU_SERVER_HOST")

    # Replace model cache paths
    pattern = PATH_PATTERNS["model_cache"]
    if re.search(pattern, content):
        changes.append(f"ENV_VAR: {pattern} → SCALAR_ROOT/models")
        if not dry_run:
            content = re.sub(pattern, REPLACEMENTS["model_cache"], content)
        replacements_made.append("MODEL_CACHE")

    # Replace data directory paths
    pattern = PATH_PATTERNS["data_dir"]
    if re.search(pattern, content):
        changes.append(f"ENV_VAR: {pattern} → SCALAR_ROOT/data")
        if not dry_run:
            content = re.sub(pattern, REPLACEMENTS["data_dir"], content)
        replacements_made.append("DATA_DIR")

    # Add required imports if replacements were made
    if replacements_made and not dry_run:
        if "import os" not in content and "from os import" not in content:
            content = "import os\n" + content
            changes.append("IMPORT: Added 'import os'")

        if "from pathlib import Path" not in content and "import pathlib" not in content:
            content = "from pathlib import Path\n" + content
            changes.append("IMPORT: Added 'from pathlib import Path'")

    return content, changes

# ============================================================================
# STRATEGY 4: Context-Aware Replacements
# ============================================================================

def context_aware_replacements(content: str, file_path: Path, dry_run: bool = True) -> Tuple[str, List[str]]:
    """Apply file-specific replacements based on context."""
    changes = []

    # YAML config files
    if file_path.suffix in ['.yaml', '.yml']:
        # Replace hardcoded paths with ${SCALAR_ROOT} template variables
        pattern = PATH_PATTERNS["second_brain_root"]
        if re.search(pattern, content):
            changes.append(f"YAML: {pattern} → ${{SCALAR_ROOT}}")
            if not dry_run:
                content = re.sub(pattern, "${SCALAR_ROOT}", content)

    # GPU config files
    if "gpu" in file_path.name.lower() or "gpu_services" in str(file_path):
        # Replace GPU IPs with environment variable references
        for gpu_key in ["gpu_server_tailscale", "gpu_server_lan"]:
            pattern = PATH_PATTERNS[gpu_key]
            if re.search(pattern, content):
                changes.append(f"GPU_CONFIG: {pattern} → ${{GPU_SERVER_HOST}}")
                if not dry_run:
                    content = re.sub(pattern, "${GPU_SERVER_HOST}", content)

    return content, changes

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def process_file(file_path: Path, dry_run: bool = True, create_backup: bool = True) -> Dict:
    """Process a single file with all replacement strategies."""

    if not file_path.exists():
        return {
            "file": str(file_path),
            "status": "SKIPPED",
            "reason": "File not found",
            "changes": [],
            "change_count": 0
        }

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        return {
            "file": str(file_path),
            "status": "ERROR",
            "reason": f"Read error: {str(e)}",
            "changes": [],
            "change_count": 0
        }

    content = original_content
    all_changes = []

    # Apply all strategies
    content, changes = remove_sys_path_calls(content, dry_run)
    all_changes.extend(changes)

    content, changes = convert_to_relative_imports(content, file_path, dry_run)
    all_changes.extend(changes)

    content, changes = extract_to_env_vars(content, dry_run)
    all_changes.extend(changes)

    content, changes = context_aware_replacements(content, file_path, dry_run)
    all_changes.extend(changes)

    # Write changes if not dry run
    if not dry_run and all_changes:
        # Create backup
        if create_backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            shutil.copy2(file_path, backup_path)

        # Write updated content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            return {
                "file": str(file_path),
                "status": "ERROR",
                "reason": f"Write error: {str(e)}",
                "changes": all_changes,
                "change_count": len(all_changes)
            }

    status = "MODIFIED" if all_changes else "NO_CHANGES"
    if dry_run and all_changes:
        status = "WOULD_MODIFY"

    return {
        "file": str(file_path.relative_to(SCALAR_ROOT)),
        "status": status,
        "changes": all_changes,
        "change_count": len(all_changes)
    }

def main():
    parser = argparse.ArgumentParser(
        description="SCALAR Path Replacement Script - Fix hardcoded paths",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually apply changes (default: dry-run)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create .backup files (default: create backups)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save report to JSON file"
    )

    args = parser.parse_args()

    dry_run = not args.execute
    create_backup = not args.no_backup

    print("=" * 80)
    print("SCALAR Path Replacement Script")
    print("=" * 80)
    print()

    if dry_run:
        print("⚠️  DRY RUN MODE - No files will be modified")
        print("   Use --execute to apply changes")
        print()

    if not SCALAR_ROOT.exists():
        print(f"❌ ERROR: SCALAR root not found: {SCALAR_ROOT}")
        print("   Run extraction script first")
        return 1

    print(f"SCALAR root: {SCALAR_ROOT}")
    print(f"Files to process: {len(FILES_TO_UPDATE)}")
    print()

    # Process all files
    results = []
    for rel_path in FILES_TO_UPDATE:
        file_path = SCALAR_ROOT / rel_path
        print(f"Processing: {rel_path}")

        result = process_file(file_path, dry_run, create_backup)
        results.append(result)

        print(f"  Status: {result['status']}")
        if result['changes']:
            print(f"  Changes: {result['change_count']}")
            for change in result['changes'][:3]:  # Show first 3
                print(f"    - {change}")
            if result['change_count'] > 3:
                print(f"    ... and {result['change_count'] - 3} more")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    total_changes = sum(r['change_count'] for r in results)
    modified_files = sum(1 for r in results if r['change_count'] > 0)
    skipped_files = sum(1 for r in results if r['status'] == 'SKIPPED')
    error_files = sum(1 for r in results if r['status'] == 'ERROR')

    print(f"Total files processed: {len(results)}")
    print(f"Files with changes: {modified_files}")
    print(f"Files skipped: {skipped_files}")
    print(f"Files with errors: {error_files}")
    print(f"Total changes: {total_changes}")
    print()

    if dry_run:
        print("This was a dry run. To apply changes, run:")
        print(f"  {__file__} --execute")
        print()
    else:
        print("✅ Changes applied successfully!")
        if create_backup:
            print("   Backup files created with .backup extension")
        print()
        print("Next steps:")
        print("1. Test imports: python -c 'from modules.config import BaseConfig'")
        print("2. Run tests: pytest tests/ -v")
        print("3. Check logs for any path-related errors")
        print()

    # Save report if requested
    if args.output:
        report = {
            "dry_run": dry_run,
            "scalar_root": str(SCALAR_ROOT),
            "total_files": len(results),
            "modified_files": modified_files,
            "total_changes": total_changes,
            "results": results
        }

        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Report saved to: {args.output}")
        print()

    return 0

if __name__ == "__main__":
    exit(main())
