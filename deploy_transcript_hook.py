#!/usr/bin/env python3
"""
Deploy transcript-path-hook-v1 update to all registered Tier1 projects.

This script:
1. Loads project registry
2. Filters for Tier1 workflow projects
3. Applies the transcript-path-hook-v1 update to each
4. Updates the project registry
5. Reports results
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


class TranscriptHookDeployer:
    """Deploys transcript-path-hook-v1 to all Tier1 projects."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.tier1_root = Path.home() / "tier1_workflow_global"
        self.registry_path = self.tier1_root / "implementation" / "project_registry.json"
        self.update_defs_path = self.tier1_root / "implementation" / "update_definitions.json"
        self.apply_script = self.tier1_root / "template" / "tools" / "apply_update.py"

        # Load registry
        with open(self.registry_path, "r") as f:
            self.registry = json.load(f)

        # Load update definitions
        with open(self.update_defs_path, "r") as f:
            self.update_defs = json.load(f)

    def get_tier1_projects(self) -> List[Dict[str, Any]]:
        """Get all Tier1 workflow projects from registry."""
        tier1_projects = []
        for project in self.registry.get("projects", []):
            # Skip tier1_workflow_global (it's the template, not a real project)
            if project.get("name") == "tier1_workflow_global":
                continue
            if project.get("workflow_type") == "Tier1":
                tier1_projects.append(project)
        return tier1_projects

    def apply_update_to_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply transcript-path-hook-v1 update to a single project.

        Returns:
            Result dictionary with status and details
        """
        project_name = project["name"]
        project_path = Path(project["path"])

        print(f"\n{'='*60}")
        print(f"Project: {project_name}")
        print(f"Path: {project_path}")
        print(f"{'='*60}")

        if not project_path.exists():
            return {
                "project": project_name,
                "status": "error",
                "message": f"Project path does not exist: {project_path}",
                "components_applied": 0,
                "components_skipped": 0,
            }

        # Get update definition
        update = None
        for u in self.update_defs.get("updates", []):
            if u["id"] == "transcript-path-hook-v1":
                update = u
                break

        if not update:
            return {
                "project": project_name,
                "status": "error",
                "message": "Update definition 'transcript-path-hook-v1' not found",
                "components_applied": 0,
                "components_skipped": 0,
            }

        # Apply each component
        components_applied = 0
        components_skipped = 0
        components_failed = 0
        errors = []

        for idx, component in enumerate(update["components"]):
            print(f"\nComponent {idx + 1}/{len(update['components'])}: {component['type']}")
            print(f"  Target: {component['target']}")

            # Run apply_update.py
            cmd = [
                "python3",
                str(self.apply_script),
                "--project-path", str(project_path),
                "--update-def", str(self.update_defs_path),
                "--update-id", "transcript-path-hook-v1",
                "--component-index", str(idx),
            ]

            if self.dry_run:
                cmd.append("--dry-run")

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                # Parse JSON result
                result_data = json.loads(result.stdout)

                if result_data.get("already_applied"):
                    print(f"  Status: Already applied (skipped)")
                    components_skipped += 1
                elif result_data.get("changes_made"):
                    print(f"  Status: Applied successfully")
                    components_applied += 1
                else:
                    print(f"  Status: No changes made")
                    components_skipped += 1

            except subprocess.CalledProcessError as e:
                print(f"  Status: FAILED")
                print(f"  Error: {e.stderr}")
                components_failed += 1
                errors.append({
                    "component_index": idx,
                    "error": e.stderr,
                })
            except Exception as e:
                print(f"  Status: FAILED")
                print(f"  Error: {str(e)}")
                components_failed += 1
                errors.append({
                    "component_index": idx,
                    "error": str(e),
                })

        # Determine overall status
        if components_failed > 0:
            status = "partial" if components_applied > 0 else "failed"
        elif components_applied > 0:
            status = "success"
        else:
            status = "already_applied"

        return {
            "project": project_name,
            "status": status,
            "components_applied": components_applied,
            "components_skipped": components_skipped,
            "components_failed": components_failed,
            "errors": errors,
        }

    def update_registry(self, project_name: str):
        """Update project registry to mark update as applied."""
        if self.dry_run:
            print(f"\n[DRY RUN] Would update registry for {project_name}")
            return

        # Find project in registry
        for project in self.registry["projects"]:
            if project["name"] == project_name:
                # Add update ID to applied_updates if not already there
                if "applied_updates" not in project:
                    project["applied_updates"] = []

                if "transcript-path-hook-v1" not in project["applied_updates"]:
                    project["applied_updates"].append("transcript-path-hook-v1")

                # Update timestamp
                from datetime import datetime
                project["last_updated"] = datetime.now().isoformat()

                break

        # Save registry
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=2)
            f.write("\n")

        print(f"✅ Registry updated for {project_name}")

    def fix_hook_permissions(self, project_path: Path):
        """Ensure capture_transcript_path.py is executable."""
        hook_path = project_path / ".claude" / "hooks" / "capture_transcript_path.py"

        if hook_path.exists():
            if self.dry_run:
                print(f"[DRY RUN] Would make {hook_path} executable")
            else:
                import stat
                current_perms = hook_path.stat().st_mode
                hook_path.chmod(current_perms | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                print(f"✅ Made {hook_path} executable")

    def deploy_all(self):
        """Deploy update to all Tier1 projects."""
        projects = self.get_tier1_projects()

        print(f"\n{'='*60}")
        print(f"Transcript Path Hook Deployment")
        print(f"{'='*60}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Found {len(projects)} Tier1 workflow projects")
        print(f"{'='*60}")

        results = []

        for project in projects:
            result = self.apply_update_to_project(project)
            results.append(result)

            # Fix permissions if update was successful
            if result["status"] in ["success", "already_applied"]:
                project_path = Path(project["path"])
                self.fix_hook_permissions(project_path)

                # Update registry
                if result["status"] == "success":
                    self.update_registry(project["name"])

        # Print summary
        self.print_summary(results)

        return results

    def print_summary(self, results: List[Dict[str, Any]]):
        """Print deployment summary."""
        print(f"\n{'='*60}")
        print("DEPLOYMENT SUMMARY")
        print(f"{'='*60}")

        total_projects = len(results)
        successful = sum(1 for r in results if r["status"] == "success")
        already_applied = sum(1 for r in results if r["status"] == "already_applied")
        partial = sum(1 for r in results if r["status"] == "partial")
        failed = sum(1 for r in results if r["status"] == "failed")
        errors = sum(1 for r in results if r["status"] == "error")

        print(f"Total projects: {total_projects}")
        print(f"  ✅ Successful: {successful}")
        print(f"  ⏭️  Already applied: {already_applied}")
        print(f"  ⚠️  Partial: {partial}")
        print(f"  ❌ Failed: {failed}")
        print(f"  🚫 Errors: {errors}")

        total_components_applied = sum(r["components_applied"] for r in results)
        total_components_skipped = sum(r["components_skipped"] for r in results)

        print(f"\nComponents:")
        print(f"  Applied: {total_components_applied}")
        print(f"  Skipped: {total_components_skipped}")

        # Show failures/errors
        if partial or failed or errors:
            print(f"\n{'='*60}")
            print("ISSUES ENCOUNTERED")
            print(f"{'='*60}")

            for result in results:
                if result["status"] in ["partial", "failed", "error"]:
                    print(f"\n❌ {result['project']}: {result['status']}")
                    if "message" in result:
                        print(f"   {result['message']}")
                    if result.get("errors"):
                        for error in result["errors"]:
                            print(f"   Component {error['component_index']}: {error['error']}")

        print(f"\n{'='*60}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy transcript-path-hook-v1 to all Tier1 projects"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )

    args = parser.parse_args()

    deployer = TranscriptHookDeployer(dry_run=args.dry_run)
    results = deployer.deploy_all()

    # Exit with error code if any deployments failed
    if any(r["status"] in ["failed", "error"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
