#!/usr/bin/env python3
"""
Surgical Update Application Script

Applies a single update component to a project file.
Supports multiple update types with idempotent checks.

Usage:
    python apply_update.py \\
        --project-path /path/to/project \\
        --update-def update_definitions.json \\
        --update-id agent-failure-reporting-protocol-v1 \\
        --component-index 0 \\
        [--dry-run]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


class UpdateApplier:
    """Applies surgical updates to project files."""

    def __init__(
        self,
        project_path: Path,
        update_definitions: Dict[str, Any],
        update_id: str,
        component_index: int,
        dry_run: bool = False,
    ):
        self.project_path = project_path
        self.update_definitions = update_definitions
        self.update_id = update_id
        self.component_index = component_index
        self.dry_run = dry_run

        # Find update definition
        self.update_def = self._find_update()
        if not self.update_def:
            raise ValueError(f"Update '{update_id}' not found in definitions")

        # Find component
        if component_index >= len(self.update_def["components"]):
            raise ValueError(
                f"Component index {component_index} out of range "
                f"(max {len(self.update_def['components']) - 1})"
            )
        self.component = self.update_def["components"][component_index]

    def _find_update(self) -> Optional[Dict[str, Any]]:
        """Find update definition by ID."""
        for update in self.update_definitions.get("updates", []):
            if update["id"] == self.update_id:
                return update
        return None

    def _run_idempotent_check(self) -> bool:
        """
        Run idempotent check command.

        Returns:
            True if update is already applied (exit code 0)
            False if update is not applied (exit code non-zero)
        """
        check_cmd = self.component.get("idempotent_check", "")
        if not check_cmd:
            # No check specified, assume not applied
            return False

        # Replace {target} placeholder with actual path
        target = self.component.get("target", "")
        target_path = self.project_path / target
        check_cmd = check_cmd.replace("{target}", str(target_path))

        try:
            result = subprocess.run(
                check_cmd,
                shell=True,
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Warning: Idempotent check failed with error: {e}", file=sys.stderr)
            return False

    def apply(self) -> Dict[str, Any]:
        """
        Apply update component.

        Returns:
            Result dictionary with status and details
        """
        result: Dict[str, Any] = {
            "status": "success",
            "update_id": self.update_id,
            "component_index": self.component_index,
            "component_type": self.component["type"],
            "target_file": self.component.get("target", "N/A"),
            "already_applied": False,
            "changes_made": False,
            "error": None,
        }

        # Run idempotent check
        if self._run_idempotent_check():
            result["already_applied"] = True
            result["changes_made"] = False
            return result

        # Apply update based on type
        component_type = self.component["type"]
        try:
            if component_type == "append_section":
                self._apply_append_section()
            elif component_type == "insert_after":
                self._apply_insert_after()
            elif component_type == "copy_if_missing":
                self._apply_copy_if_missing()
            elif component_type == "patch_line":
                self._apply_patch_line()
            elif component_type == "patch_execute_workflow":
                self._apply_patch_execute_workflow()
            elif component_type == "merge_json":
                self._apply_merge_json()
            else:
                raise ValueError(f"Unknown component type: {component_type}")

            result["changes_made"] = True

        except Exception as e:
            result["status"] = "failure"
            result["error"] = str(e)

        return result

    def _apply_append_section(self) -> None:
        """
        Apply append_section update type.

        Inserts section content BEFORE specified marker.
        """
        target = self.component["target"]
        marker = self.component["marker"]
        section_file = self.component["section_file"]

        target_path = self.project_path / target

        # Resolve section file path (relative to template root)
        # section_file is like "implementation/updates/agent-failure-protocol-backend.md"
        # We need to find the template root (parent of project_path if project is template,
        # or ~/tier1_workflow_global)
        template_root = Path.home() / "tier1_workflow_global"
        section_path = template_root / section_file

        if not target_path.exists():
            raise FileNotFoundError(f"Target file not found: {target_path}")

        if not section_path.exists():
            raise FileNotFoundError(f"Section file not found: {section_path}")

        # Read target file
        with open(target_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find marker
        marker_index = None
        for i, line in enumerate(lines):
            if marker in line:
                marker_index = i
                break

        if marker_index is None:
            raise ValueError(f"Marker not found in target file: {marker}")

        # Read section content
        with open(section_path, "r", encoding="utf-8") as f:
            section_content = f.read()

        # Ensure section content ends with newline
        if not section_content.endswith("\n"):
            section_content += "\n"

        # Add blank line after section (before marker)
        section_content += "\n"

        if self.dry_run:
            print(f"[DRY RUN] Would insert {len(section_content)} chars before line {marker_index}", file=sys.stderr)
            return

        # Insert section before marker
        lines.insert(marker_index, section_content)

        # Write back
        with open(target_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def _apply_insert_after(self) -> None:
        """
        Apply insert_after update type.

        Inserts content AFTER first line matching pattern.
        """
        target = self.component["target"]
        pattern = self.component["pattern"]
        content = self.component["content"]

        target_path = self.project_path / target

        if not target_path.exists():
            raise FileNotFoundError(f"Target file not found: {target_path}")

        # Read target file
        with open(target_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find pattern
        pattern_index = None
        for i, line in enumerate(lines):
            if pattern in line:
                pattern_index = i
                break

        if pattern_index is None:
            raise ValueError(f"Pattern not found in target file: {pattern}")

        # Ensure content ends with newline
        if not content.endswith("\n"):
            content += "\n"

        if self.dry_run:
            print(f"[DRY RUN] Would insert after line {pattern_index}: {content.strip()}", file=sys.stderr)
            return

        # Insert after pattern line
        lines.insert(pattern_index + 1, content)

        # Write back
        with open(target_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def _apply_copy_if_missing(self) -> None:
        """
        Apply copy_if_missing update type.

        Copies file from source to target (only if target doesn't exist).
        """
        target = self.component["target"]
        source = self.component["source"]

        target_path = self.project_path / target

        # Source is relative to template root
        template_root = Path.home() / "tier1_workflow_global"
        source_path = template_root / source

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        if target_path.exists():
            # Already exists, skip (idempotent check should have caught this)
            return

        # Create parent directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            print(f"[DRY RUN] Would copy {source_path} to {target_path}", file=sys.stderr)
            return

        # Copy file
        shutil.copy2(source_path, target_path)

    def _apply_patch_line(self) -> None:
        """
        Apply patch_line update type.

        Replaces exact line match with new line.
        """
        target = self.component["target"]
        old_line = self.component["old_line"]
        new_line = self.component["new_line"]

        target_path = self.project_path / target

        if not target_path.exists():
            raise FileNotFoundError(f"Target file not found: {target_path}")

        # Read target file
        with open(target_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find old line
        matches = []
        for i, line in enumerate(lines):
            if line.strip() == old_line.strip():
                matches.append(i)

        if len(matches) == 0:
            raise ValueError(f"Old line not found in target file: {old_line}")

        if len(matches) > 1:
            raise ValueError(
                f"Ambiguous match: old line appears {len(matches)} times. "
                "Make pattern more specific."
            )

        match_index = matches[0]

        # Ensure new line has same line ending as old line
        if not new_line.endswith("\n") and lines[match_index].endswith("\n"):
            new_line += "\n"

        if self.dry_run:
            print(f"[DRY RUN] Would replace line {match_index}: {old_line.strip()} -> {new_line.strip()}", file=sys.stderr)
            return

        # Replace line
        lines[match_index] = new_line

        # Write back
        with open(target_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def _apply_patch_execute_workflow(self) -> None:
        """
        Apply patch_execute_workflow update type.

        Performs search-and-replace operations on the target file.
        This is similar to patch_line but supports multi-line replacements.
        """
        target = self.component["target"]
        operations = self.component.get("operations", [])

        target_path = self.project_path / target

        if not target_path.exists():
            raise FileNotFoundError(f"Target file not found: {target_path}")

        # Read target file as a single string (not lines)
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply each operation
        for operation in operations:
            search = operation.get("search", "")
            replace = operation.get("replace", "")

            if not search:
                raise ValueError("Search pattern is required for patch_execute_workflow")

            # Count occurrences
            count = content.count(search)

            if count == 0:
                # Pattern not found - this might be okay if already patched
                # Check if the idempotent check would pass
                continue
            elif count > 1:
                raise ValueError(
                    f"Ambiguous match: search pattern appears {count} times. "
                    "Make pattern more specific."
                )

            # Replace (exactly once)
            content = content.replace(search, replace, 1)

        if self.dry_run:
            print(f"[DRY RUN] Would apply {len(operations)} search-replace operations", file=sys.stderr)
            return

        # Only write if content changed
        if content != original_content:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)

    def _apply_merge_json(self) -> None:
        """
        Apply merge_json update type.

        Merges JSON data into the target file. If target doesn't exist,
        creates it with the merge data.
        """
        target = self.component["target"]
        merge_data = self.component.get("merge_data", {})

        target_path = self.project_path / target

        # Create parent directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing JSON or start with empty dict
        if target_path.exists():
            with open(target_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        # Deep merge the data
        merged_data = self._deep_merge(existing_data, merge_data)

        if self.dry_run:
            print(f"[DRY RUN] Would merge JSON data into {target_path}", file=sys.stderr)
            return

        # Write merged JSON
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, indent=2)
            f.write("\n")  # Add trailing newline

    def _deep_merge(self, base: dict, updates: dict) -> dict:
        """
        Deep merge two dictionaries.

        Args:
            base: Base dictionary
            updates: Updates to merge into base

        Returns:
            Merged dictionary (new dict, doesn't modify inputs)
        """
        result = base.copy()

        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Overwrite or add new key
                result[key] = value

        return result


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Apply surgical update to project file"
    )
    parser.add_argument(
        "--project-path",
        type=Path,
        required=True,
        help="Project root directory",
    )
    parser.add_argument(
        "--update-def",
        type=Path,
        required=True,
        help="Path to update_definitions.json",
    )
    parser.add_argument(
        "--update-id",
        type=str,
        required=True,
        help="Update ID to apply",
    )
    parser.add_argument(
        "--component-index",
        type=int,
        required=True,
        help="Component index (0-based)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview mode (don't modify files)",
    )

    args = parser.parse_args()

    # Validate project path
    if not args.project_path.is_dir():
        print(f"Error: Project path not found: {args.project_path}", file=sys.stderr)
        sys.exit(1)

    # Load update definitions
    if not args.update_def.exists():
        print(f"Error: Update definitions file not found: {args.update_def}", file=sys.stderr)
        sys.exit(1)

    with open(args.update_def, "r", encoding="utf-8") as f:
        update_definitions = json.load(f)

    # Create applier and apply update
    try:
        applier = UpdateApplier(
            project_path=args.project_path,
            update_definitions=update_definitions,
            update_id=args.update_id,
            component_index=args.component_index,
            dry_run=args.dry_run,
        )

        result = applier.apply()

        # Output result as JSON
        print(json.dumps(result, indent=2))

        # Exit with appropriate code
        if result["status"] == "failure":
            sys.exit(1)

    except Exception as e:
        result = {
            "status": "failure",
            "update_id": args.update_id,
            "component_index": args.component_index,
            "error": str(e),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
