---
description: "List all tasks with optional filtering"
argument-hint: "[status] [type]"
allowed-tools: [Bash]
---

## List Tasks

Parse optional filters from $ARGUMENTS:
- If empty: list all tasks
- If one argument: treat as status filter (backlog, current, completed)
- If two arguments: first=status, second=type

Run bash command to find and display tasks:

```bash
STATUS_FILTER=""
TYPE_FILTER=""

# Parse arguments
if [ -n "$ARGUMENTS" ]; then
  ARG1=$(echo "$ARGUMENTS" | awk '{print $1}')
  ARG2=$(echo "$ARGUMENTS" | awk '{print $2}')

  if [ -n "$ARG1" ]; then
    STATUS_FILTER="$ARG1"
  fi
  if [ -n "$ARG2" ]; then
    TYPE_FILTER="$ARG2"
  fi
fi

# Determine search directories
if [ -z "$STATUS_FILTER" ]; then
  SEARCH_DIRS=".tasks/backlog .tasks/current .tasks/completed"
else
  SEARCH_DIRS=".tasks/${STATUS_FILTER}"
fi

# Find and display tasks
echo "📋 Tasks:"
echo ""

TASK_COUNT=0

for dir in $SEARCH_DIRS; do
  if [ ! -d "$dir" ]; then
    continue
  fi

  find "$dir" -name "*.task.md" 2>/dev/null | while read task_file; do
    # Extract metadata from frontmatter
    ID=$(grep "^id:" "$task_file" | sed 's/id: *//')
    TITLE=$(grep "^title:" "$task_file" | sed 's/title: *//')
    TYPE=$(grep "^type:" "$task_file" | sed 's/type: *//')
    PRIORITY=$(grep "^priority:" "$task_file" | sed 's/priority: *//')
    STATUS=$(basename $(dirname "$task_file"))

    # Apply type filter if specified
    if [ -n "$TYPE_FILTER" ] && [ "$TYPE" != "$TYPE_FILTER" ]; then
      continue
    fi

    echo "[$STATUS] $ID - $TITLE (type: $TYPE, priority: $PRIORITY)"
    TASK_COUNT=$((TASK_COUNT + 1))
  done
done | sort

echo ""
echo "Total: ${TASK_COUNT} tasks"
```
