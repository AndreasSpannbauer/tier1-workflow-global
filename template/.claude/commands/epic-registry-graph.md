---
description: "Generate Mermaid dependency graph of epics"
allowed-tools: [Read, Bash]
---

# Epic Registry Dependency Graph

Generate Mermaid diagram showing epic dependencies.

---

## Step 1: Generate Graph

```bash
python3 << 'EOF'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from tools.epic_registry import load_registry

try:
    registry = load_registry()

    if not registry.data.epics:
        print("ℹ️  No epics in registry")
        sys.exit(0)

    print("```mermaid")
    print("graph TD")
    print("")

    # Define nodes
    for epic in registry.data.epics:
        # Color by status
        color = {
            "defined": "#f0f0f0",
            "prepared": "#fff3cd",
            "ready": "#d1ecf1",
            "implemented": "#d4edda",
            "archived": "#e0e0e0",
        }.get(epic.status.value, "#ffffff")

        label = f"{epic.epic_id}: {epic.title[:30]}"
        print(f"  {epic.epic_id}[\"{label}\"]")
        print(f"  style {epic.epic_id} fill:{color}")

    print("")

    # Define edges (dependencies)
    for epic in registry.data.epics:
        for blocked_by in epic.dependencies.blocked_by:
            print(f"  {blocked_by} --> {epic.epic_id}")

        for integrates_with in epic.dependencies.integrates_with:
            if integrates_with not in epic.dependencies.blocked_by:  # Avoid duplicates
                print(f"  {integrates_with} -.-> {epic.epic_id}")

    print("```")
    print("")

    # Legend
    print("**Legend:**")
    print("- Solid arrow (→): Blocking dependency (must complete first)")
    print("- Dashed arrow (-.->): Integration relationship")
    print("")
    print("**Status Colors:**")
    print("- Gray: Defined")
    print("- Yellow: Prepared")
    print("- Blue: Ready")
    print("- Green: Implemented")
    print("")

except FileNotFoundError:
    print("❌ Epic registry not found")
    print("")
    print("Initialize registry first:")
    print("  /epic-registry-init")

EOF
```

---

## Usage

Copy the Mermaid code and paste into:
- GitHub markdown (renders automatically)
- VS Code with Mermaid extension
- https://mermaid.live for interactive editing
