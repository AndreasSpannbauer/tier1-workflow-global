---
description: "Analyze master spec coverage and suggest next epics"
allowed-tools: [Read, Bash]
---

# Epic Registry Coverage Analysis

Analyze which master spec requirements are covered by epics and suggest gaps.

---

## Step 1: Calculate Coverage

```bash
python3 << 'EOF'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from tools.epic_registry import load_registry, calculate_coverage, suggest_next_epic_from_coverage

try:
    registry = load_registry()
    coverage = calculate_coverage(registry.data, Path.cwd())

    print("="*70)
    print("MASTER SPEC COVERAGE ANALYSIS")
    print("="*70)
    print("")

    print(f"Master spec: {registry.data.master_spec_path}")
    print(f"Total requirements: {coverage.total_requirements}")
    print(f"Covered by epics:   {coverage.covered_by_epics}")
    print(f"Coverage:           {coverage.coverage_percentage}%")
    print("")

    if coverage.total_requirements == 0:
        print("⚠️  No requirements found in master spec")
        print("")
        print("Expected format:")
        print("  - REQ-001: Description")
        print("  - REQ-002: Another requirement")
        print("")
    else:
        # Progress bar
        progress = int(coverage.coverage_percentage / 5)
        bar = "█" * progress + "░" * (20 - progress)
        print(f"Progress: [{bar}] {coverage.coverage_percentage}%")
        print("")

    if coverage.uncovered_requirements:
        print("="*70)
        print(f"UNCOVERED REQUIREMENTS ({len(coverage.uncovered_requirements)})")
        print("="*70)
        print("")

        for req in coverage.uncovered_requirements:
            print(f"  - {req}")

        print("")

        # Suggestions
        suggestions = suggest_next_epic_from_coverage(coverage)
        if suggestions:
            print("="*70)
            print("SUGGESTED NEXT EPICS")
            print("="*70)
            print("")
            print("Consider creating epics to address:")
            for req in suggestions:
                print(f"  - {req}")
            print("")

    # Save coverage to registry
    registry.data.master_spec_coverage = coverage
    registry.save()

    print("✅ Coverage saved to registry")
    print("")

except FileNotFoundError:
    print("❌ Epic registry not found")
    print("")
    print("Initialize registry first:")
    print("  /epic-registry-init")

EOF
```

---

## Next Steps

```
View registry status: /epic-registry-status
Create next epic:     /spec-epic "Epic Title"
```
