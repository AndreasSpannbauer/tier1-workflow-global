---
description: "View task details"
argument-hint: "<task-id>"
allowed-tools: [Read, Bash]
---

## Get Task

Find task file by ID:

```bash
TASK_FILE=$(find .tasks -name "${ARGUMENTS}*.task.md" | head -1)
```

If not found:
```
❌ Task ${ARGUMENTS} not found

Available tasks:
```

Run: `/task-list`

If found, use Read tool to display the task file content.

Also display:
```
📁 Location: ${TASK_FILE}
```
