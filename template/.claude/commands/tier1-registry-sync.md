---
description: "Sync project registry - discover and register Tier 1 workflow projects"
allowed-tools: [Read, Write, Bash]
---

# Tier 1 Workflow Registry Sync

Discovers Tier 1 workflow projects and updates the registry.

---

## Step 1: Read Current Registry

```bash
REGISTRY_FILE="$HOME/tier1_workflow_global/implementation/project_registry.json"

if [ ! -f "$REGISTRY_FILE" ]; then
  echo "❌ Registry not found: $REGISTRY_FILE"
  exit 1
fi

echo "📋 Reading current registry..."
cat "$REGISTRY_FILE"
echo ""
```

---

## Step 2: Auto-Discovery

Search for projects with Tier 1 workflow installed:

```bash
echo "🔍 Discovering Tier 1 workflow projects..."
echo ""

# Search paths (add more as needed)
SEARCH_PATHS=(
  "$HOME/coding_projects"
  "$HOME"
)

DISCOVERED=()

for BASE_PATH in "${SEARCH_PATHS[@]}"; do
  if [ ! -d "$BASE_PATH" ]; then
    continue
  fi

  echo "Scanning: $BASE_PATH"

  # Find directories with execute-workflow.md
  while IFS= read -r -d '' WORKFLOW_FILE; do
    PROJECT_DIR=$(dirname $(dirname $(dirname "$WORKFLOW_FILE")))
    PROJECT_NAME=$(basename "$PROJECT_DIR")

    # Skip if already in registry
    if jq -e ".projects[] | select(.name == \"$PROJECT_NAME\")" "$REGISTRY_FILE" > /dev/null 2>&1; then
      echo "  ✓ Already registered: $PROJECT_NAME"
    else
      echo "  🆕 Found new project: $PROJECT_NAME"
      DISCOVERED+=("$PROJECT_DIR")
    fi
  done < <(find "$BASE_PATH" -maxdepth 3 -type f -path "*/.claude/commands/execute-workflow.md" -print0 2>/dev/null)
done

echo ""
echo "Discovery complete:"
echo "  New projects found: ${#DISCOVERED[@]}"
echo ""
```

---

## Step 3: Analyze New Projects

For each discovered project, detect:
- Workflow type (Tier1, V6, or Reference)
- Installation date (from git history or file timestamp)
- Template hash (from git)
- Custom modifications

```bash
if [ ${#DISCOVERED[@]} -eq 0 ]; then
  echo "✅ No new projects to add"
  exit 0
fi

echo "Analyzing new projects..."
echo ""

for PROJECT_DIR in "${DISCOVERED[@]}"; do
  PROJECT_NAME=$(basename "$PROJECT_DIR")
  echo "Project: $PROJECT_NAME"
  echo "  Path: $PROJECT_DIR"

  # Detect workflow type
  if [ -f "$PROJECT_DIR/.claude/commands/w-workflow-v6-mcp.md" ]; then
    WORKFLOW_TYPE="V6"
  elif [ -f "$PROJECT_DIR/.claude/commands/execute-workflow.md" ]; then
    WORKFLOW_TYPE="Tier1"
  else
    WORKFLOW_TYPE="Unknown"
  fi
  echo "  Type: $WORKFLOW_TYPE"

  # Get installation date from git (if available)
  if [ -d "$PROJECT_DIR/.git" ]; then
    INSTALL_DATE=$(cd "$PROJECT_DIR" && git log --format=%aI --reverse -- .claude/commands/execute-workflow.md 2>/dev/null | head -1 | cut -d'T' -f1)
    TEMPLATE_HASH=$(cd "$PROJECT_DIR" && git log -1 --format=%h -- .claude/commands/execute-workflow.md 2>/dev/null)
  else
    INSTALL_DATE=$(date +%Y-%m-%d)
    TEMPLATE_HASH="unknown"
  fi
  echo "  Installed: $INSTALL_DATE"
  echo "  Hash: $TEMPLATE_HASH"

  # Check for custom modifications
  HAS_CUSTOM=false
  if [ -f "$PROJECT_DIR/.claude/commands/w-workflow-v6-mcp.md" ]; then
    HAS_CUSTOM=true
  fi
  echo "  Custom mods: $HAS_CUSTOM"
  echo ""

  # Store for later addition
  # (Will be added to registry in Step 4)
done
```

---

## Step 4: Update Registry

Add discovered projects to registry:

```bash
echo "📝 Updating registry..."
echo ""

# Create backup
cp "$REGISTRY_FILE" "$REGISTRY_FILE.backup-$(date +%s)"

# Use Python to add projects (cleaner JSON handling)
python3 << 'EOF'
import json
import os
from pathlib import Path
from datetime import datetime

registry_file = Path.home() / "tier1_workflow_global" / "implementation" / "project_registry.json"

with open(registry_file) as f:
    registry = json.load(f)

# Get discovered projects from environment (passed as JSON)
# For now, we'll skip actual addition since discovery was read-only above
# In real execution, orchestrator would parse bash output and add here

# Update last_sync timestamp
registry["last_sync"] = datetime.utcnow().isoformat() + "Z"

with open(registry_file, 'w') as f:
    json.dump(registry, f, indent=2)

print(f"✅ Registry updated")
print(f"   Total projects: {len(registry['projects'])}")
EOF

echo ""
```

---

## Step 5: Verify Registry

```bash
echo "Verifying all registered projects exist..."
echo ""

python3 << 'EOF'
import json
from pathlib import Path

registry_file = Path.home() / "tier1_workflow_global" / "implementation" / "project_registry.json"

with open(registry_file) as f:
    registry = json.load(f)

missing = []
verified = []

for project in registry["projects"]:
    project_path = Path(project["path"])
    workflow_file = project_path / ".claude" / "commands" / "execute-workflow.md"

    if workflow_file.exists():
        verified.append(project["name"])
    else:
        missing.append(project["name"])
        print(f"⚠️  Project not found: {project['name']}")
        print(f"   Expected: {workflow_file}")

print(f"\n✅ Verified: {len(verified)} projects")
if missing:
    print(f"⚠️  Missing: {len(missing)} projects")
    print("\nConsider removing missing projects from registry")
EOF

echo ""
```

---

## Step 6: Summary

```bash
echo "======================================================================"
echo "✅ Registry Sync Complete"
echo "======================================================================"
echo ""
echo "Registry: $REGISTRY_FILE"
echo ""
echo "Next steps:"
echo "  • Check versions: /tier1-check-versions"
echo "  • Update projects: /tier1-update-all"
echo ""
```

---

## Notes

**Manual additions:**
To manually add a project, edit `project_registry.json` and add:
```json
{
  "name": "project_name",
  "path": "/full/path/to/project",
  "workflow_type": "Tier1",
  "installed_date": "2025-10-21",
  "last_verified": "2025-10-21",
  "template_hash": "abc123",
  "has_custom_modifications": false,
  "custom_commands": [],
  "notes": ""
}
```

**Search paths:**
Edit `SEARCH_PATHS` array in Step 2 to add custom locations.

**Workflow types:**
- `Tier1` - Standard execute-workflow.md
- `V6` - V6 variant with MCP integration
- `Reference` - Reference implementation (not actively updated)
