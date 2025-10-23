---
description: "Initialize epic registry in current project"
allowed-tools: [Read, Write, Bash]
---

# Initialize Epic Registry

Creates `.tasks/epic_registry.json` for epic lifecycle tracking.

---

## Step 1: Verify Project Structure

```bash
if [ ! -d ".tasks" ]; then
  echo "❌ .tasks directory not found"
  echo "   This command must be run from project root"
  exit 1
fi

if [ -f ".tasks/epic_registry.json" ]; then
  echo "⚠️  Epic registry already exists"
  echo "   .tasks/epic_registry.json"
  echo ""
  echo "Delete it first if you want to re-initialize:"
  echo "  rm .tasks/epic_registry.json"
  exit 1
fi
```

---

## Step 2: Detect Project Information

```bash
# Get project name from directory
PROJECT_NAME=$(basename "$PWD")

# Detect GitHub repo (if git remote exists)
GITHUB_REPO=""
if git remote get-url origin &> /dev/null; then
  REMOTE_URL=$(git remote get-url origin)
  # Extract user/repo from URL
  GITHUB_REPO=$(echo "$REMOTE_URL" | sed 's/.*github.com[:/]\(.*\)\.git/\1/' | sed 's/.*github.com[:/]\(.*\)/\1/')
fi

echo "Project name: $PROJECT_NAME"
echo "GitHub repo: ${GITHUB_REPO:-<not detected>}"
echo ""
```

---

## Step 3: Create Registry

```bash
python3 << 'EOF'
import sys
from pathlib import Path
from datetime import datetime

# Add tools to path
sys.path.insert(0, str(Path.cwd()))

from tools.epic_registry import create_registry
import os

project_name = os.environ.get("PROJECT_NAME", "unknown")
github_repo = os.environ.get("GITHUB_REPO") or None

registry = create_registry(project_name, Path.cwd(), github_repo)

print(f"✅ Epic registry created")
print(f"   File: .tasks/epic_registry.json")
print(f"   Project: {project_name}")
if github_repo:
    print(f"   GitHub: {github_repo}")

EOF
```

---

## Step 4: Scan for Existing Epics (Optional)

```bash
echo ""
echo "Scanning for existing epics..."
echo ""

# Find epic directories
EPIC_DIRS=$(find .tasks/backlog .tasks/current .tasks/completed -name "EPIC-*" -type d 2>/dev/null | sort)

if [ -z "$EPIC_DIRS" ]; then
  echo "No existing epics found (empty project)"
else
  echo "Found existing epics:"
  echo "$EPIC_DIRS"
  echo ""
  echo "⚠️  To import these epics into the registry, run:"
  echo "   /epic-registry-sync"
fi

echo ""
```

---

## Completion

```
✅ Epic registry initialized

File: .tasks/epic_registry.json

Next steps:
  1. Import existing epics: /epic-registry-sync
  2. Create first epic: /spec-epic "Epic Title"
  3. View registry status: /epic-registry-status
```

---

## Notes

- Registry is automatically updated by `/spec-epic` and `/execute-workflow`
- Use `/epic-registry-sync` to fix inconsistencies
- Registry is JSON for programmatic access (Python, jq)
