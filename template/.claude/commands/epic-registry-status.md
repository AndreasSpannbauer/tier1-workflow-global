---
description: "Show epic registry status and statistics"
allowed-tools: [Read, Bash]
---

# Epic Registry Status

Display registry statistics and epic breakdown.

---

## Step 1: Load Registry

```bash
python3 << 'EOF'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from tools.epic_registry import load_registry

try:
    registry = load_registry()

    print("="*70)
    print("EPIC REGISTRY STATUS")
    print("="*70)
    print("")
    print(f"Project: {registry.data.project_name}")
    if registry.data.github_repo:
        print(f"GitHub: {registry.data.github_repo}")
    print(f"Registry: .tasks/epic_registry.json")
    print("")

    # Statistics
    stats = registry.data.statistics
    print("="*70)
    print("STATISTICS")
    print("="*70)
    print(f"Total epics:     {stats.total_epics}")
    print(f"  Defined:       {stats.defined}")
    print(f"  Prepared:      {stats.prepared}")
    print(f"  Ready:         {stats.ready}")
    print(f"  Implemented:   {stats.implemented}")
    print(f"  Archived:      {stats.archived}")
    print("")
    print(f"Next epic number: {registry.data.next_epic_number}")
    print("")

    # Coverage
    if registry.data.master_spec_coverage:
        cov = registry.data.master_spec_coverage
        print("="*70)
        print("MASTER SPEC COVERAGE")
        print("="*70)
        print(f"Total requirements: {cov.total_requirements}")
        print(f"Covered by epics:   {cov.covered_by_epics}")
        print(f"Coverage:           {cov.coverage_percentage}%")
        print("")
        if cov.uncovered_requirements:
            print(f"Uncovered ({len(cov.uncovered_requirements)}):")
            for req in cov.uncovered_requirements[:10]:
                print(f"  - {req}")
            if len(cov.uncovered_requirements) > 10:
                print(f"  ... and {len(cov.uncovered_requirements) - 10} more")
        print("")

    # Epic breakdown by status
    if registry.data.epics:
        print("="*70)
        print("EPIC BREAKDOWN")
        print("="*70)
        print("")

        for status_name in ["defined", "prepared", "ready", "implemented", "archived"]:
            epics = [e for e in registry.data.epics if e.status.value == status_name]
            if epics:
                print(f"{status_name.upper()} ({len(epics)}):")
                for epic in epics:
                    tags_str = f" [{', '.join(epic.tags)}]" if epic.tags else ""
                    github_str = f" (#{epic.github_issue})" if epic.github_issue else ""
                    print(f"  - {epic.epic_id}: {epic.title}{tags_str}{github_str}")
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

## Commands

```
View detailed epic: /task-get EPIC-001
Update coverage:    /epic-registry-coverage
Sync registry:      /epic-registry-sync
```
