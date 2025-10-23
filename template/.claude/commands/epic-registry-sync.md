---
description: "Sync epic registry with filesystem (fix inconsistencies)"
allowed-tools: [Read, Write, Bash]
---

# Epic Registry Sync

Scan `.tasks/` directories and sync with registry. Detects orphaned epics and inconsistencies.

---

## Step 1: Scan Filesystem

```bash
echo "🔍 Scanning .tasks/ directories..."
echo ""

# Find all epic directories
FOUND_EPICS=$(find .tasks/backlog .tasks/current .tasks/completed -name "EPIC-*" -type d 2>/dev/null | sort)

if [ -z "$FOUND_EPICS" ]; then
  echo "ℹ️  No epic directories found"
  exit 0
fi

echo "Found epic directories:"
echo "$FOUND_EPICS"
echo ""
```

---

## Step 2: Compare with Registry

```bash
python3 << 'EOF'
import sys
from pathlib import Path
from glob import glob

sys.path.insert(0, str(Path.cwd()))

from tools.epic_registry import load_registry

try:
    registry = load_registry()

    # Get epic directories from filesystem
    fs_epic_dirs = set()
    for pattern in [".tasks/backlog/EPIC-*", ".tasks/current/EPIC-*", ".tasks/completed/EPIC-*"]:
        for path in glob(pattern):
            if Path(path).is_dir():
                fs_epic_dirs.add(path)

    # Get epic directories from registry
    reg_epic_dirs = {epic.directory for epic in registry.data.epics}

    # Find orphaned (in filesystem, not in registry)
    orphaned = fs_epic_dirs - reg_epic_dirs

    # Find missing (in registry, not in filesystem)
    missing = reg_epic_dirs - fs_epic_dirs

    print("="*70)
    print("SYNC ANALYSIS")
    print("="*70)
    print("")

    if orphaned:
        print(f"⚠️  Orphaned epics (in filesystem, not in registry): {len(orphaned)}")
        for path in sorted(orphaned):
            print(f"  - {path}")
        print("")
        print("Add to registry with:")
        print("  /spec-epic <title> (for new epics)")
        print("")

    if missing:
        print(f"⚠️  Missing epics (in registry, not in filesystem): {len(missing)}")
        for path in sorted(missing):
            print(f"  - {path}")
        print("")
        print("These epics may have been moved or deleted.")
        print("")

    if not orphaned and not missing:
        print("✅ Registry is in sync with filesystem")
        print("")

    print("="*70)

except FileNotFoundError:
    print("❌ Epic registry not found")
    print("")
    print("Initialize registry first:")
    print("  /epic-registry-init")

EOF
```

---

## Step 3: Auto-Fix (Optional)

```
Manual intervention required for orphaned/missing epics.

To add orphaned epic to registry:
  1. Read epic spec.md
  2. Use registry.add_epic() with correct metadata
  3. Save registry

To remove missing epic from registry:
  1. Archive or delete from registry
  2. Save registry
```
