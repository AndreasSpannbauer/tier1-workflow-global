---
description: "Create new task with automatic ID generation"
argument-hint: "<type> <title>"
allowed-tools: [Write, Bash, Read]
---

## Task Creation

Parse $ARGUMENTS:
- First word = type (feature, bug, chore, refactor, docs)
- Rest = title

Example: "feature Add user authentication"
→ type=feature, title="Add user authentication"

### Validation

Extract type and title from arguments:

```bash
# Parse arguments
ARGS="$ARGUMENTS"
TYPE=$(echo "$ARGS" | awk '{print $1}')
TITLE=$(echo "$ARGS" | cut -d' ' -f2-)
```

Validate type is one of: feature, bug, chore, refactor, docs

If invalid:
```
❌ Invalid type: ${TYPE}
Valid types: feature, bug, chore, refactor, docs

Usage: /task-create <type> <title>
Example: /task-create feature "Add OAuth login"
```

Stop execution.

### Generate Task ID

Use bash to find the next ID:

```bash
TYPE_UPPER=$(echo "${TYPE}" | tr '[:lower:]' '[:upper:]')

# Find all task files with this type
LAST_ID=$(find .tasks/backlog .tasks/current .tasks/completed -name "${TYPE_UPPER}-*.task.md" 2>/dev/null | \
  sed "s/.*${TYPE_UPPER}-\([0-9]*\).*/\1/" | \
  sort -n | \
  tail -1)

# Calculate next ID
NEXT_ID=$((${LAST_ID:-0} + 1))
TASK_ID=$(printf "${TYPE_UPPER}-%03d" $NEXT_ID)
```

### Create Task File

Read template from `.tasks/templates/task.md.j2`

Substitute variables using sed or manual string replacement:
- `{{ id }}` → ${TASK_ID}
- `{{ title }}` → ${TITLE}
- `{{ type }}` → ${TYPE}
- `{{ priority }}` → "medium"
- `{{ status }}` → "backlog"
- `{{ created }}` → $(date +%Y-%m-%d)
- `{{ area }}` → "general"

Write to `.tasks/backlog/${TASK_ID}.task.md`

### Display Result

```
✅ Created task: ${TASK_ID}
📁 Location: .tasks/backlog/${TASK_ID}.task.md
📋 Title: ${TITLE}
🏷️  Type: ${TYPE}

Next steps:
- Edit task file to add details: code .tasks/backlog/${TASK_ID}.task.md
- View task: /task-get ${TASK_ID}
- Start work: /task-update ${TASK_ID} current
```
