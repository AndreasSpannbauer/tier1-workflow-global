---
description: "Check Tier 1 workflow versions across all registered projects"
allowed-tools: [Read, Bash]
---

# Tier 1 Workflow - Check Versions

Quickly check which projects are up to date with the latest workflow template.

---

## Step 1: Read Registry and Template

```bash
REGISTRY_FILE="$HOME/tier1_workflow_global/implementation/project_registry.json"
TEMPLATE_FILE="$HOME/tier1_workflow_global/template/.claude/commands/execute-workflow.md"

if [ ! -f "$REGISTRY_FILE" ]; then
  echo "❌ Registry not found: $REGISTRY_FILE"
  echo "   Run: /tier1-registry-sync"
  exit 1
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "❌ Template not found: $TEMPLATE_FILE"
  exit 1
fi

echo "Tier 1 Workflow Version Check"
echo "======================================================================"
echo ""
```

---

## Step 2: Compute Template Hash

```bash
TEMPLATE_HASH=$(md5sum "$TEMPLATE_FILE" | cut -d' ' -f1)
TEMPLATE_SIZE=$(wc -l < "$TEMPLATE_FILE")

echo "Template (source of truth):"
echo "  File: $TEMPLATE_FILE"
echo "  Hash: $TEMPLATE_HASH"
echo "  Size: $TEMPLATE_SIZE lines"
echo ""
```

---

## Step 3: Check Each Project

```bash
echo "Checking registered projects..."
echo "======================================================================"
echo ""

python3 << 'EOF'
import json
from pathlib import Path
import hashlib

def compute_md5(file_path):
    """Compute MD5 hash of file"""
    import hashlib
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

registry_file = Path.home() / "tier1_workflow_global" / "implementation" / "project_registry.json"
template_hash = "${TEMPLATE_HASH}"

with open(registry_file) as f:
    registry = json.load(f)

up_to_date = []
outdated = []
missing = []
skipped = []

for project in registry["projects"]:
    name = project["name"]
    path = Path(project["path"])
    workflow_type = project["workflow_type"]

    # Skip source template
    if name == "tier1_workflow_global":
        skipped.append(name)
        continue

    # Skip reference projects
    if workflow_type == "Reference":
        skipped.append(name)
        continue

    # Check workflow file
    workflow_file = path / ".claude" / "commands" / "execute-workflow.md"

    if not workflow_file.exists():
        print(f"❌ {name}")
        print(f"   Status: MISSING")
        print(f"   Path: {workflow_file}")
        print("")
        missing.append(name)
        continue

    # Compute hash
    project_hash = compute_md5(workflow_file)
    project_size = len(workflow_file.read_text().splitlines())

    if project_hash == template_hash:
        print(f"✅ {name}")
        print(f"   Status: UP TO DATE")
        print(f"   Hash: {project_hash}")
        print(f"   Size: {project_size} lines")
        print("")
        up_to_date.append(name)
    else:
        print(f"⚠️  {name}")
        print(f"   Status: OUTDATED")
        print(f"   Hash: {project_hash} (expected: {template_hash})")
        print(f"   Size: {project_size} lines (template: ${TEMPLATE_SIZE} lines)")
        print(f"   Type: {workflow_type}")
        if project.get("has_custom_modifications"):
            print(f"   Note: Has custom modifications")
        print("")
        outdated.append(name)

# Summary
print("======================================================================")
print("Summary:")
print(f"  ✅ Up to date: {len(up_to_date)}")
print(f"  ⚠️  Outdated: {len(outdated)}")
print(f"  ❌ Missing: {len(missing)}")
print(f"  ➖ Skipped: {len(skipped)} (source template or reference)")
print("======================================================================")
print("")

if outdated:
    print("Outdated projects:")
    for name in outdated:
        print(f"  • {name}")
    print("")
    print("To update all projects:")
    print("  /tier1-update-all --dry-run  (preview changes)")
    print("  /tier1-update-all            (apply updates)")
    print("")

if missing:
    print("Missing workflow files:")
    for name in missing:
        print(f"  • {name}")
    print("")
    print("These projects may need manual attention or registry cleanup.")
    print("")

if not outdated and not missing:
    print("✅ All projects are up to date!")
    print("")
EOF
```

---

## Step 4: Registry Status

```bash
echo "Registry status:"
echo ""

python3 << 'EOF'
import json
from pathlib import Path
from datetime import datetime

registry_file = Path.home() / "tier1_workflow_global" / "implementation" / "project_registry.json"

with open(registry_file) as f:
    registry = json.load(f)

print(f"  Registry file: {registry_file}")
print(f"  Schema version: {registry.get('schema_version', 'unknown')}")
print(f"  Template version: {registry.get('template_version', 'unknown')}")
print(f"  Last sync: {registry.get('last_sync', 'never')}")
print(f"  Total projects: {len(registry['projects'])}")
print("")

# Show project types
from collections import Counter
types = Counter(p["workflow_type"] for p in registry["projects"])
print("  Project types:")
for ptype, count in types.items():
    print(f"    {ptype}: {count}")

EOF

echo ""
echo "To sync registry with filesystem:"
echo "  /tier1-registry-sync"
echo ""
```

---

## Next Steps

```bash
echo "======================================================================"
echo "Version check complete"
echo "======================================================================"
```

---

## Notes

**Template hash:** Uses MD5 hash to detect changes to workflow file

**Skipped projects:**
- `tier1_workflow_global` (source template)
- Projects with `workflow_type: Reference`

**Outdated detection:**
- Compares MD5 hash of project file vs template
- Line count shown for reference
- Custom modifications flag indicated

**Fast:** No file modifications, just reads and compares

**Use before updates:** Run this before `/tier1-update-all` to see what needs updating
