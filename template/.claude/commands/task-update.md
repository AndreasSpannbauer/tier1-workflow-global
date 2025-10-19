---
description: "Update task status (moves file between directories)"
argument-hint: "<task-id> <new-status>"
allowed-tools: [Read, Write, Bash]
---

## Update Task Status

Parse $ARGUMENTS:
- First argument = task_id
- Second argument = new_status (backlog, current, completed)

Example: "FEATURE-001 current"

### Validation

Extract arguments:

```bash
TASK_ID=$(echo "$ARGUMENTS" | awk '{print $1}')
NEW_STATUS=$(echo "$ARGUMENTS" | awk '{print $2}')
```

Validate new_status is one of: backlog, current, completed

If invalid:
```
❌ Invalid status: ${NEW_STATUS}
Valid statuses: backlog, current, completed

Usage: /task-update <task-id> <status>
Example: /task-update FEATURE-001 current
```

### Find Task File

```bash
TASK_FILE=$(find .tasks -name "${TASK_ID}*.task.md" | head -1)
```

If not found, display error and stop.

### Read Current Content

Use Read tool to get current task file content.

### Update Frontmatter

Update the status field and add/update timestamp:

Use Write tool to create updated content with:
- status field changed to new_status
- updated_at field set to current timestamp

### Move File

Calculate new path:

```bash
FILENAME=$(basename "$TASK_FILE")
NEW_PATH=".tasks/${NEW_STATUS}/${FILENAME}"
```

Write the updated content to NEW_PATH.

Remove old file:

```bash
rm "$TASK_FILE"
```

### Sync Status to GitHub (CORE)

If task has GitHub metadata in frontmatter (issue_number, issue_url), sync to GitHub:

```python
from pathlib import Path
import sys
sys.path.insert(0, './tools')

from github_integration.issue_sync_gh import sync_status_to_github_simple

# Extract issue_number from frontmatter
# (Already have task content from Read step)

# Check if task has github: section with issue_number
issue_number = None
for line in content.split('\n'):
    if 'issue_number:' in line:
        issue_number = line.split(':', 1)[1].strip()
        break

if issue_number:
    try:
        # For epic directories
        if Path(NEW_PATH).is_dir():
            epic_dir = Path(NEW_PATH)
        else:
            # For simple task files, use parent directory
            epic_dir = Path(NEW_PATH).parent

        sync_status_to_github_simple(TASK_ID, NEW_STATUS, epic_dir)
        print(f"✅ Synced status to GitHub: {NEW_STATUS}")
        print(f"   - Updated issue #{issue_number} labels")
        print(f"   - Posted status change comment")
    except Exception as e:
        print(f"⚠️  GitHub sync failed (non-blocking): {e}")
        print(f"   Task updated locally, but GitHub not synced")
else:
    print(f"ℹ️  No GitHub issue linked (create one with /spec-epic or manually)")
```

### Display Result

```
✅ Updated ${TASK_ID}: [old_status] → ${NEW_STATUS}
📁 New location: ${NEW_PATH}

Status: ${NEW_STATUS}
Updated: $(date)
```
