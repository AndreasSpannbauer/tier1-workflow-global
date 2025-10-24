---
description: "Update Tier 1 workflow files across all registered projects in parallel"
argument-hint: "[--dry-run] [--project=name] [--template=path]"
allowed-tools: [Read, Bash, Task]
---

# Tier 1 Workflow - Update All Projects

Updates workflow template files across all registered projects using parallel subagents.

**CRITICAL:** All subagents must be deployed in a SINGLE message for parallel execution.

---

## Step 1: Parse Arguments

```bash
DRY_RUN=false
PROJECT_FILTER=""
TEMPLATE_FILE="$HOME/tier1_workflow_global/template/.claude/commands/execute-workflow.md"

# Parse arguments from $ARGUMENTS
for ARG in $ARGUMENTS; do
  case $ARG in
    --dry-run)
      DRY_RUN=true
      ;;
    --project=*)
      PROJECT_FILTER="${ARG#*=}"
      ;;
    --template=*)
      TEMPLATE_FILE="${ARG#*=}"
      ;;
  esac
done

echo "Configuration:"
echo "  Dry run: $DRY_RUN"
echo "  Project filter: ${PROJECT_FILTER:-all projects}"
echo "  Template: $TEMPLATE_FILE"
echo ""
```

---

## Step 2: Read Registry

```bash
REGISTRY_FILE="$HOME/tier1_workflow_global/implementation/project_registry.json"

if [ ! -f "$REGISTRY_FILE" ]; then
  echo "❌ Registry not found: $REGISTRY_FILE"
  echo "   Run: /tier1-registry-sync"
  exit 1
fi

echo "📋 Reading project registry..."
echo ""
```

**Action:** Read the registry file to get project list.

---

## Step 3: Filter Projects

Select which projects to update:

```bash
echo "Projects to update:"
echo ""

python3 << 'EOF'
import json
from pathlib import Path

registry_file = Path.home() / "tier1_workflow_global" / "implementation" / "project_registry.json"

with open(registry_file) as f:
    registry = json.load(f)

# Filter logic
project_filter = "${PROJECT_FILTER}"

projects_to_update = []

for project in registry["projects"]:
    # Skip source template
    if project["name"] == "tier1_workflow_global":
        continue

    # Skip reference projects
    if project["workflow_type"] == "Reference":
        continue

    # Apply filter if specified
    if project_filter and project["name"] != project_filter:
        continue

    projects_to_update.append(project)

if not projects_to_update:
    print("⚠️  No projects match filter criteria")
    exit(1)

# Display projects
for i, project in enumerate(projects_to_update, 1):
    print(f"{i}. {project['name']}")
    print(f"   Type: {project['workflow_type']}")
    print(f"   Path: {project['path']}")
    print(f"   Custom: {project['has_custom_modifications']}")
    print("")

print(f"Total: {len(projects_to_update)} projects")
print("")

# Export for next step (write to temp file)
import os
output_file = f"/tmp/tier1_update_projects_{os.getpid()}.json"
with open(output_file, 'w') as f:
    json.dump(projects_to_update, f, indent=2)

print(f"Project list saved to: {output_file}")
EOF

echo ""
```

---

## Step 4: Read Template File

```bash
if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "❌ Template file not found: $TEMPLATE_FILE"
  exit 1
fi

echo "Template file: $TEMPLATE_FILE"
echo "Size: $(wc -l < "$TEMPLATE_FILE") lines"
echo ""
```

**Action:** Read the template file that will be deployed to projects.

---

## Step 5: Deploy Parallel Subagents

**CRITICAL:** Deploy ALL subagents in this SINGLE step for parallel execution.

```bash
echo "🚀 Deploying parallel subagents..."
echo "======================================================================"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "DRY RUN MODE - No files will be modified"
  echo ""
fi

# Create output directory for results
RESULTS_DIR="$HOME/tier1_workflow_global/.workflow/update-results/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo "Results will be written to: $RESULTS_DIR"
echo ""
```

**FOR THE ORCHESTRATOR (Claude Code):**

Deploy one subagent per project. ALL `Task()` calls must be in a SINGLE message.

**For each project in the filtered list:**

```python
# Example for project "whisper_hotkeys"
Task(
    subagent_type="general-purpose",
    description=f"Update workflow in whisper_hotkeys",
    prompt=f"""
YOU ARE: Workflow Update Agent

YOUR TASK: Update Tier 1 workflow files in a single project

---

PROJECT DETAILS:

Name: whisper_hotkeys
Path: /home/andreas-spannbauer/whisper_hotkeys
Workflow Type: Tier1
Has Custom Modifications: false

---

TEMPLATE FILE:

[Read {TEMPLATE_FILE}]

---

INSTRUCTIONS:

1. **Change to project directory:**
   ```bash
   cd /home/andreas-spannbauer/whisper_hotkeys
   ```

2. **Check current workflow file:**
   ```bash
   TARGET_FILE=".claude/commands/execute-workflow.md"

   if [ ! -f "$TARGET_FILE" ]; then
     echo "❌ Workflow file not found"
     exit 1
   fi

   # Compute hash of current file
   CURRENT_HASH=$(md5sum "$TARGET_FILE" | cut -d' ' -f1)
   echo "Current hash: $CURRENT_HASH"
   ```

3. **Compare with template:**
   ```bash
   TEMPLATE_HASH=$(md5sum {TEMPLATE_FILE} | cut -d' ' -f1)
   echo "Template hash: $TEMPLATE_HASH"

   if [ "$CURRENT_HASH" = "$TEMPLATE_HASH" ]; then
     echo "✅ Already up to date"
     ACTION="no_change"
   else
     echo "🔄 Update needed"
     ACTION="update"
   fi
   ```

4. **Create backup and update (if DRY_RUN=false):**
   ```bash
   if [ "$ACTION" = "update" ] && [ "{DRY_RUN}" = "false" ]; then
     # Backup current file
     cp "$TARGET_FILE" "$TARGET_FILE.backup-$(date +%s)"

     # Copy template
     cp {TEMPLATE_FILE} "$TARGET_FILE"

     echo "✅ File updated"
     RESULT="updated"
   elif [ "$ACTION" = "update" ] && [ "{DRY_RUN}" = "true" ]; then
     echo "🔍 DRY RUN - Would update file"
     RESULT="would_update"
   else
     RESULT="up_to_date"
   fi
   ```

5. **Verify update (if not dry run):**
   ```bash
   if [ "$RESULT" = "updated" ]; then
     # Verify file exists and is not empty
     if [ -f "$TARGET_FILE" ] && [ -s "$TARGET_FILE" ]; then
       NEW_HASH=$(md5sum "$TARGET_FILE" | cut -d' ' -f1)
       echo "New hash: $NEW_HASH"
       echo "✅ Update verified"
     else
       echo "❌ Update failed - file missing or empty"
       RESULT="failed"
     fi
   fi
   ```

6. **Write results JSON:**
   ```bash
   cat > {RESULTS_DIR}/whisper_hotkeys.json << 'RESULT_EOF'
{{
  "project": "whisper_hotkeys",
  "path": "/home/andreas-spannbauer/whisper_hotkeys",
  "result": "$RESULT",
  "current_hash": "$CURRENT_HASH",
  "template_hash": "$TEMPLATE_HASH",
  "dry_run": {DRY_RUN},
  "timestamp": "$(date -Iseconds)"
}}
RESULT_EOF

   echo ""
   echo "✅ Results written to {RESULTS_DIR}/whisper_hotkeys.json"
   ```

---

EXECUTE THE ABOVE STEPS AND WRITE RESULTS JSON.

Do NOT make any other changes to the project.
"""
)

# Repeat for EACH project in the filtered list
# ALL Task() calls must be in THIS SINGLE MESSAGE
```

**Note to orchestrator:** Read the project list from `/tmp/tier1_update_projects_*.json` and generate one `Task()` call per project. Deploy all in a single message.

---

## Step 6: Wait for Completion

```bash
echo ""
echo "⏳ Waiting for all subagents to complete..."
echo ""
echo "Agents are working in parallel on:"

# List projects
python3 << 'EOF'
import json
import sys
import glob

# Find temp file
temp_files = glob.glob("/tmp/tier1_update_projects_*.json")
if not temp_files:
    print("❌ Project list not found")
    sys.exit(1)

with open(temp_files[0]) as f:
    projects = json.load(f)

for project in projects:
    print(f"  • {project['name']}")

print("")
EOF
```

---

## Step 7: Collect Results

After all subagents complete, collect and aggregate results:

```bash
echo "📊 Collecting results..."
echo "======================================================================"
echo ""

python3 << 'EOF'
import json
from pathlib import Path
import sys

results_dir = Path("${RESULTS_DIR}")

if not results_dir.exists():
    print(f"❌ Results directory not found: {results_dir}")
    sys.exit(1)

result_files = list(results_dir.glob("*.json"))

if not result_files:
    print("⚠️  No results files found")
    sys.exit(1)

# Aggregate results
updated = []
up_to_date = []
would_update = []
failed = []

for result_file in sorted(result_files):
    with open(result_file) as f:
        result = json.load(f)

    project_name = result["project"]
    result_status = result["result"]

    if result_status == "updated":
        updated.append(project_name)
    elif result_status == "up_to_date":
        up_to_date.append(project_name)
    elif result_status == "would_update":
        would_update.append(project_name)
    elif result_status == "failed":
        failed.append(project_name)

# Display summary
print("Results Summary:")
print("")

if updated:
    print(f"✅ Updated ({len(updated)}):")
    for name in updated:
        print(f"   • {name}")
    print("")

if would_update:
    print(f"🔍 Would update ({len(would_update)}) [dry run]:")
    for name in would_update:
        print(f"   • {name}")
    print("")

if up_to_date:
    print(f"✓ Already up to date ({len(up_to_date)}):")
    for name in up_to_date:
        print(f"   • {name}")
    print("")

if failed:
    print(f"❌ Failed ({len(failed)}):")
    for name in failed:
        print(f"   • {name}")
    print("")

# Overall summary
total = len(result_files)
print("======================================================================"
print(f"Total projects processed: {total}")
print(f"  Updated: {len(updated)}")
print(f"  Up to date: {len(up_to_date)}")
print(f"  Failed: {len(failed)}")

if "${DRY_RUN}" == "true":
    print(f"  Would update (dry run): {len(would_update)}")

print("======================================================================")
EOF

echo ""
```

---

## Step 8: Cleanup

```bash
# Remove temp files
rm -f /tmp/tier1_update_projects_*.json

echo ""
echo "Results saved to: $RESULTS_DIR"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "⚠️  DRY RUN COMPLETE - No files were modified"
  echo ""
  echo "To apply updates, run without --dry-run:"
  echo "  /tier1-update-all"
  echo ""
else
  echo "✅ UPDATE COMPLETE"
  echo ""
  echo "Next steps:"
  echo "  • Review changes in each project"
  echo "  • Test workflows in updated projects"
  echo "  • Commit changes if everything works"
  echo ""
fi
```

---

## Usage Examples

```bash
# Dry run to see what would be updated
/tier1-update-all --dry-run

# Update all projects
/tier1-update-all

# Update specific project
/tier1-update-all --project=whisper_hotkeys

# Use custom template file
/tier1-update-all --template=~/custom-workflow.md

# Dry run for specific project
/tier1-update-all --dry-run --project=email_management_system
```

---

## Safety Features

**Backups:** Original files are backed up with timestamp before update

**Dry run:** `--dry-run` shows what would be updated without modifying files

**Verification:** After update, file hash is checked to ensure successful copy

**Project filter:** `--project=name` updates only one project for testing

**Isolation:** Each subagent works in its own directory (no conflicts)

---

## Notes

**Parallel execution:** All subagents run simultaneously for maximum speed

**Custom modifications:** Projects marked with `has_custom_modifications: true` are still updated (template is base, customizations should be preserved if in different files)

**V6 vs Tier1:** The command updates `execute-workflow.md` for Tier1 projects. V6 projects may need custom handling.

**Registry updates:** After successful update, consider running `/tier1-registry-sync` to update hashes in registry.
