# V6 Tier 1 - Final Implementation Plan (Simplified & Robust)

**Date:** 2025-10-18
**Philosophy:** Maximum value, minimum complexity, zero fragility

---

## Executive Summary

**What Tier 1 Provides:**
- ✅ Complete task management (CRUD operations)
- ✅ Hierarchical epic specs with interactive creation
- ✅ GitHub integration for stakeholder visibility
- ✅ Contract DEFINITION in plain YAML/text (human-readable)
- ✅ Progress tracking via GitHub comments
- ✅ Professional appearance with zero configuration

**What Tier 1 Does NOT Include:**
- ❌ MCP server (not needed for per-project work)
- ❌ Cross-project queries (each project standalone)
- ❌ JSON Schema generation (that's validation, Tier 2)
- ❌ Type compilation (that's testing, Tier 2/3)
- ❌ Multi-phase workflow orchestration
- ❌ Quality gates and loops
- ❌ Graph-server integration
- ❌ Testing infrastructure

**Setup Time:** 1-2 hours per project
**Maintenance:** ~15 minutes/month (virtually zero)
**Fragility:** Minimal (bash + files + GitHub CLI)

---

## Core Principle: Specs Do the Work

The value comes from **having a detailed spec**, not from complex automation.

### Tier 1: Definition (Human Work)

**In spec.md, you write:**

```markdown
## Data Contracts

### User Authentication Request
```yaml
endpoint: POST /api/auth/login
request:
  email: string         # User's email address
  password: string      # Plain text password (hashed by server)
  remember_me: boolean  # Optional, default false

response_success:
  token: string         # JWT token, expires in 24h
  user_id: string       # UUID
  email: string

response_error:
  error: string
  message: string
```

### User Profile Response
```yaml
endpoint: GET /api/users/{user_id}
response:
  user_id: string
  email: string
  name: string
  created_at: datetime  # ISO 8601 format
  roles: array<string>  # ["admin", "user"]
```
```

**This is part of spec creation** - You and Claude define what the API should look like.

### Tier 2: Generation (Validation)

**A script reads spec.md and generates:**
- JSON Schema files in `contracts/`
- TypeScript types in `frontend/src/types/`
- Python Pydantic models in `backend/src/models/`
- Compilation verification

**This is for validation/testing**, not core workflow.

### Why This Separation Works

✅ **Tier 1 is robust** - Just markdown files, no fragile generation
✅ **Specs are readable** - Stakeholders can review YAML contracts
✅ **Tier 2 is optional** - Only add if TypeScript/Python validation provides value
✅ **No runtime dependency** - Specs work without generation
✅ **Gradual adoption** - Start with definition, add generation later

---

## Architecture: Commands-Only + GitHub

### File Structure

```
<project>/
├── .tasks/
│   ├── backlog/
│   │   ├── EPIC-007-SemanticSearch/
│   │   │   ├── spec.md                    # WHAT/WHY + contract definitions
│   │   │   ├── architecture.md            # HOW (system design)
│   │   │   ├── task.md                    # Workflow metadata + GitHub sync info
│   │   │   ├── contracts/                 # Contract definitions (YAML)
│   │   │   │   └── api-contracts.yaml     # Defined during spec creation
│   │   │   └── implementation-details/    # Prescriptive plans
│   │   │       └── file-tasks.md
│   │   └── FEATURE-012.task.md
│   ├── current/
│   │   └── FEATURE-011.task.md
│   ├── completed/
│   └── templates/
│       ├── task.md.j2
│       ├── spec.md.j2
│       └── architecture.md.j2
│
├── .claude/
│   ├── commands/
│   │   ├── task-create.md        # Bash-based task creation
│   │   ├── task-get.md           # Read and display task
│   │   ├── task-update.md        # Update status + GitHub sync
│   │   ├── task-list.md          # Find and list tasks
│   │   └── spec-epic.md          # Interactive spec creation + GitHub
│   │
│   └── output-styles/
│       └── spec-architect.md     # Spec creation behavior
│
└── tools/
    └── github_integration/       # Copied from email_management_system
        ├── gh_cli_wrapper.py
        ├── issue_sync_gh.py
        ├── issue_mapper.py
        ├── label_manager.py
        ├── progress_reporter.py
        └── models.py
```

### Key Design Decisions

**1. No MCP Server**
- Bash commands handle all operations
- ID generation via bash script
- YAML parsing via simple grep/sed (or Python helper if needed)
- No server to maintain, restart, or debug

**2. GitHub as Presentation Layer**
- Local `.tasks/` files = source of truth
- GitHub Issues = mirror for humans
- Uses existing `gh` CLI authentication (zero config)
- Non-blocking (failures don't stop work)

**3. Contract Definition (Not Generation)**
- Specs include YAML contract definitions
- Human-readable, part of planning process
- No automatic JSON Schema generation in Tier 1
- Stakeholders can review contracts during spec creation

**4. Per-Project Focus**
- Each project is standalone
- No cross-project queries needed
- Commands work independently in each repo
- Copy commands once, customize per project

---

## Implementation: Week-by-Week Plan

### Week 1: Core Task Management (No GitHub Yet)

**Goal:** Validate bash-based task management works

**Day 1-2: Directory Structure + Templates**

Create directory structure:
```bash
mkdir -p .tasks/{backlog,current,completed,templates}
mkdir -p .claude/{commands,output-styles,templates}
```

Create task template (`.tasks/templates/task.md.j2`):
```markdown
---
id: {{ id }}
title: {{ title }}
type: {{ type }}
priority: {{ priority }}
status: {{ status }}
created: {{ created }}
area: {{ area }}
---

# {{ id }}: {{ title }}

## Problem Statement

[Describe what this task solves]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Implementation Notes

[Technical details, links, references]

## Progress

- [ ] Task created
- [ ] Implementation complete
- [ ] Tested locally
- [ ] Ready for review
```

Create epic spec template (`.tasks/templates/spec.md.j2`):
```markdown
---
epic_id: {{ epic_id }}
title: {{ title }}
type: epic
status: draft
priority: {{ priority }}
created: {{ created }}
---

# {{ epic_id }}: {{ title }}

## Problem Statement

### User Pain Point
[What problem does this solve?]

### Current State
[What's the manual workaround today?]

### Desired State
[What should the automated solution do?]

## User Scenarios

### Scenario 1: [Name]
1. User does X
2. System does Y
3. User sees Z
4. **Expected outcome:** [Success criteria]

### Scenario 2: [Name]
1. [Step 1]
2. [Step 2]
3. **Expected outcome:** [Success criteria]

## Functional Requirements

### FR-1: [Requirement Name]
**Description:** [What the system MUST do]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

### FR-2: [Requirement Name]
**Description:** [What the system MUST do]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

## Data Contracts (Definitions Only)

### [Contract 1 Name]
```yaml
# Define what data looks like (human-readable YAML)
endpoint: POST /api/endpoint
request:
  field1: string
  field2: number
response:
  result: object
  status: string
```

### [Contract 2 Name]
```yaml
# Another contract definition
```

## Technical Constraints

- **Performance:** [Requirements]
- **Security:** [Considerations]
- **Compatibility:** [Constraints]

## Out of Scope

- [Explicitly NOT included]
- [Future considerations]

## Success Metrics

- [Measurable outcome 1]
- [Measurable outcome 2]
```

**Day 3: task-create Command**

`.claude/commands/task-create.md`:
```markdown
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

Validate type is one of: feature, bug, chore, refactor, docs

If invalid:
```
❌ Invalid type: {type}
Valid types: feature, bug, chore, refactor, docs

Usage: /task-create <type> <title>
Example: /task-create feature "Add OAuth login"
```

Stop execution.

### Generate Task ID

```bash
TYPE_UPPER=$(echo "${type}" | tr '[:lower:]' '[:upper:]')
LAST_ID=$(find .tasks/backlog .tasks/current .tasks/completed -name "${TYPE_UPPER}-*.task.md" 2>/dev/null | \
  sed "s/.*${TYPE_UPPER}-\([0-9]*\).*/\1/" | \
  sort -n | \
  tail -1)
NEXT_ID=$((${LAST_ID:-0} + 1))
TASK_ID=$(printf "${TYPE_UPPER}-%03d" $NEXT_ID)
```

### Load Template

Read `.tasks/templates/task.md.j2`

Substitute variables:
- `{{ id }}` → ${TASK_ID}
- `{{ title }}` → ${title}
- `{{ type }}` → ${type}
- `{{ priority }}` → "medium"
- `{{ status }}` → "backlog"
- `{{ created }}` → $(date +%Y-%m-%d)
- `{{ area }}` → "general"

### Write Task File

Use Write tool to create `.tasks/backlog/${TASK_ID}.task.md` with substituted content.

### Display Result

```
✅ Created task: ${TASK_ID}
📁 Location: .tasks/backlog/${TASK_ID}.task.md
📋 Title: ${title}

Next steps:
- Edit task file to add details
- Run /task-get ${TASK_ID} to view
- Run /task-update ${TASK_ID} current to start work
```
```

**Day 4: task-get and task-list Commands**

`.claude/commands/task-get.md`:
```markdown
---
description: "Read and display task"
argument-hint: "<task-id>"
allowed-tools: [Read, Bash]
---

## Get Task

Find task file:
```bash
TASK_FILE=$(find .tasks -name "${ARGUMENTS}*.task.md" | head -1)
```

If not found:
```
❌ Task ${ARGUMENTS} not found

Check available tasks with: /task-list
```

If found, use Read tool to display task file.

Display location:
```
📁 Location: ${TASK_FILE}
```
```

`.claude/commands/task-list.md`:
```markdown
---
description: "List tasks with optional filtering"
argument-hint: "[status] [type]"
allowed-tools: [Bash]
---

## List Tasks

Parse optional filters from $ARGUMENTS:
- If no arguments: list all
- If one argument: treat as status filter (backlog, current, completed)
- If two arguments: first=status, second=type

### Find Tasks

```bash
if [ -z "$STATUS_FILTER" ]; then
  SEARCH_DIRS=".tasks/backlog .tasks/current .tasks/completed"
else
  SEARCH_DIRS=".tasks/${STATUS_FILTER}"
fi

# Find all task files
find $SEARCH_DIRS -name "*.task.md" 2>/dev/null | while read task_file; do
  # Extract ID and title from frontmatter
  ID=$(grep "^id:" "$task_file" | sed 's/id: //')
  TITLE=$(grep "^title:" "$task_file" | sed 's/title: //')
  TYPE=$(grep "^type:" "$task_file" | sed 's/type: //')
  PRIORITY=$(grep "^priority:" "$task_file" | sed 's/priority: //')
  STATUS=$(basename $(dirname "$task_file"))

  # Apply type filter if specified
  if [ -n "$TYPE_FILTER" ] && [ "$TYPE" != "$TYPE_FILTER" ]; then
    continue
  fi

  echo "[$STATUS] $ID - $TITLE (type: $TYPE, priority: $PRIORITY)"
done | sort
```

### Display Results

Format output as table:
```
📋 Tasks:

[backlog] FEATURE-001 - Add user authentication (type: feature, priority: high)
[backlog] FEATURE-002 - Implement search (type: feature, priority: medium)
[current] BUG-001 - Fix login redirect (type: bug, priority: critical)
[completed] CHORE-001 - Update dependencies (type: chore, priority: low)

Total: 4 tasks
```
```

**Day 5: task-update Command**

`.claude/commands/task-update.md`:
```markdown
---
description: "Update task status (moves file between directories)"
argument-hint: "<task-id> <new-status>"
allowed-tools: [Read, Write, Bash]
---

## Update Task Status

Parse $ARGUMENTS:
- First argument = task_id
- Second argument = new_status (backlog, current, completed)

Validate new_status is one of: backlog, current, completed

### Find Task File

```bash
TASK_FILE=$(find .tasks -name "${task_id}*.task.md" | head -1)
```

If not found, error and stop.

### Read Current Task

Use Read tool to get current content.

### Update Frontmatter

Find the `status:` line in frontmatter and replace with new status:

```bash
# Update status in frontmatter
sed -i "s/^status: .*/status: ${new_status}/" content

# Update updated_at timestamp
sed -i "s/^updated_at: .*/updated_at: $(date -Iseconds)/" content
# If updated_at doesn't exist, add it after status line
if ! grep -q "^updated_at:" content; then
  sed -i "/^status:/a updated_at: $(date -Iseconds)" content
fi
```

### Move File

```bash
FILENAME=$(basename "$TASK_FILE")
NEW_PATH=".tasks/${new_status}/${FILENAME}"

# Write updated content to new location
# (Use Write tool with NEW_PATH and updated content)

# Remove old file
rm "$TASK_FILE"
```

### Display Result

```
✅ Updated ${task_id}: backlog → ${new_status}
📁 New location: ${NEW_PATH}

Status: ${new_status}
Updated: $(date)
```

Note: GitHub sync will be added in Week 2.
```

**Deliverable Week 1:**
- Working task CRUD operations
- Epic structure templates
- All operations via bash commands
- No external dependencies

---

### Week 2: GitHub Integration

**Goal:** Make tasks visible on GitHub

**Day 1: Copy GitHub Integration Module**

```bash
# From email_management_system
cp -r ~/coding_projects/email_management_system/tools/github_integration ./tools/

# Verify gh CLI authentication
gh auth status
# Should show: ✓ Logged in to github.com
```

**Day 2: Initialize GitHub Labels (One-Time)**

Run once per repository:

```bash
python3 << 'EOF'
from tools.github_integration.label_manager import get_label_taxonomy
from tools.github_integration.gh_cli_wrapper import create_label

taxonomy = get_label_taxonomy()
for category, labels in taxonomy.items():
    for label in labels:
        try:
            create_label(label.name, label.color, label.description)
            print(f"✅ Created label: {label.name}")
        except Exception as e:
            print(f"⚠️ Label {label.name}: {e}")

print("\n✅ All labels initialized")
EOF
```

This creates 24 standard labels:
- **Status:** planned, in-progress, review, blocked, completed
- **Type:** epic, feature, task, sub-task
- **Domain:** backend, frontend, database, testing, docs
- **Priority:** critical, high, medium, low

**Day 3: Update task-create to Sync GitHub**

Add to `.claude/commands/task-create.md` after task creation:

```markdown
### Optional: Create GitHub Issue

Ask user:
```
Create GitHub issue for visibility? (yes/no)
```

If yes:
```python
from pathlib import Path
from tools.github_integration.gh_cli_wrapper import create_issue

# For simple tasks, create basic issue
issue = create_issue(
    title=f"{TASK_ID}: {title}",
    body=f"Task created via Claude Code\n\nType: {type}\nPriority: medium",
    labels=[f"type:{type}", "status:planned"]
)

print(f"✅ GitHub Issue: {issue['url']}")

# Update task.md frontmatter with GitHub metadata
# (Add github: section to frontmatter)
```

Display issue URL.
```

**Day 4: Create spec-epic Command with GitHub Integration**

`.claude/commands/spec-epic.md`:
```markdown
---
description: "Create epic with interactive spec refinement and GitHub issue"
argument-hint: "<title>"
allowed-tools: [Write, Read, Bash, AskUserQuestion]
---

## Epic Spec Creation

Switch to Spec Architect output style (if available):
```
/output-style Spec Architect
```

### Round 1: Problem Understanding

Use AskUserQuestion to gather:

**Question 1:** What user pain point does this solve?
**Question 2:** What is the current manual workaround?
**Question 3:** What is the desired automated behavior?
**Question 4:** What is the expected impact (users affected, time saved)?

[Wait for user responses]

### Round 2: Scope Definition

Based on Round 1 answers, ask:

**Question 5:** Which existing components will this integrate with?
**Question 6:** What new components are needed?
**Question 7:** What data sources are involved?
**Question 8:** What are the edge cases?
**Question 9:** What are the non-goals (explicitly out of scope)?

[Wait for user responses]

### Round 3: Technical Constraints

**Question 10:** What are the performance requirements?
**Question 11:** What are the security considerations?
**Question 12:** What are compatibility constraints?

[Wait for user responses]

### Generate Epic ID

```bash
LAST_EPIC=$(find .tasks/backlog -name "EPIC-*.task.md" -o -name "EPIC-*" -type d | \
  sed 's/.*EPIC-\([0-9]*\).*/\1/' | \
  sort -n | \
  tail -1)
NEXT_EPIC=$((${LAST_EPIC:-0} + 1))
EPIC_ID=$(printf "EPIC-%03d" $NEXT_EPIC)
```

### Create Epic Directory Structure

```bash
EPIC_SLUG=$(echo "$ARGUMENTS" | sed 's/ //g' | sed 's/[^a-zA-Z0-9]//g')
EPIC_DIR=".tasks/backlog/${EPIC_ID}-${EPIC_SLUG}"

mkdir -p "${EPIC_DIR}"/{contracts,implementation-details,research}
```

### Write spec.md

Use Write tool to create `${EPIC_DIR}/spec.md` with:
- Frontmatter (epic_id, title, status, priority, created)
- Problem Statement (from Round 1)
- User Scenarios (from Round 1-2)
- Functional Requirements (from Round 2)
- Data Contracts (YAML definitions from Round 2-3)
- Technical Constraints (from Round 3)
- Out of Scope (from Round 2)

### Write architecture.md

Create `${EPIC_DIR}/architecture.md` with template:
```markdown
---
epic_id: ${EPIC_ID}
title: ${title}
type: architecture
version: 1.0
---

# ${EPIC_ID}: Architecture

## System Overview

[High-level description of system design]

## Components

### Component 1: [Name]
**Purpose:** [What it does]
**Technology:** [Stack]
**Dependencies:** [What it depends on]

### Component 2: [Name]
[...]

## Data Flow

```
User → Frontend → API → Service Layer → Database
                  ↓
              External APIs
```

## Database Schema

[Tables, relationships, indexes]

## API Endpoints

[List endpoints with methods and purposes]

## Security Considerations

[Authentication, authorization, data protection]

## Performance Considerations

[Caching, optimization strategies]
```

### Write task.md

Create `${EPIC_DIR}/task.md`:
```markdown
---
id: ${EPIC_ID}
title: ${title}
type: epic
priority: high
status: backlog
created: $(date +%Y-%m-%d)
area: general
---

# ${EPIC_ID}: ${title}

[Link to spec.md and architecture.md]

See:
- [Specification](./spec.md)
- [Architecture](./architecture.md)
- [Implementation Details](./implementation-details/)
```

### Create GitHub Issue

```python
from pathlib import Path
from tools.github_integration.issue_sync_gh import create_github_issue_from_epic

epic_dir = Path("${EPIC_DIR}")
issue_url = create_github_issue_from_epic("${EPIC_ID}", epic_dir)

if issue_url:
    print(f"✅ GitHub Issue created: {issue_url}")
else:
    print(f"⚠️ GitHub issue creation failed (check logs, non-blocking)")
```

The `create_github_issue_from_epic` function:
1. Reads spec.md and architecture.md
2. Extracts summary (problem, requirements)
3. Formats as GitHub issue body
4. Creates issue with labels (epic, domain, priority)
5. Updates task.md frontmatter with GitHub metadata

### Display Completion

```
✅ Epic created: ${EPIC_ID}
📁 Location: ${EPIC_DIR}

Created files:
- spec.md (WHAT/WHY - user scenarios, requirements, contracts)
- architecture.md (HOW - system design, components)
- task.md (workflow metadata)
- contracts/ (contract definitions)
- implementation-details/ (empty, ready for planning)

🔗 GitHub Issue: ${issue_url}

Next steps:
1. Review and refine spec.md
2. Add implementation details to implementation-details/file-tasks.md
3. Start implementation: /task-update ${EPIC_ID} current
```
```

**Day 5: Update task-update to Sync Status**

Add to `.claude/commands/task-update.md` after moving file:

```markdown
### Sync Status to GitHub

If task has GitHub metadata in frontmatter:

```python
from pathlib import Path
from tools.github_integration.issue_sync_gh import sync_status_to_github_simple

# Read task frontmatter to get GitHub metadata
# (grep for "github:" section and issue_number)

if issue_number:
    epic_dir = Path(NEW_PATH).parent  # For epics
    # Or just the file's directory for simple tasks

    sync_status_to_github_simple(task_id, new_status, epic_dir)
    print(f"✅ Synced status to GitHub: {new_status}")
```

This updates:
- GitHub issue labels (removes old status:*, adds new status:*)
- Posts comment: "Status updated: backlog → in-progress"
- Updates task.md last_synced timestamp
```

**Deliverable Week 2:**
- GitHub integration fully working
- Tasks sync to GitHub automatically
- Progress visible to stakeholders
- Zero configuration (uses gh CLI)

---

### Week 3: Rollout to Multiple Projects

**Goal:** Install Tier 1 in all active projects

**Day 1: Create Installation Script**

`setup-tier1.sh`:
```bash
#!/bin/bash
# Tier 1 Installation Script
# Usage: ./setup-tier1.sh

set -e

PROJECT_ROOT=$(pwd)

echo "🚀 Installing V6 Tier 1 Task Management..."
echo "📂 Project: $PROJECT_ROOT"
echo ""

# 1. Verify gh CLI authentication
echo "1️⃣ Verifying GitHub CLI authentication..."
if ! gh auth status &>/dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi
echo "✅ GitHub CLI authenticated"
echo ""

# 2. Create directory structure
echo "2️⃣ Creating directory structure..."
mkdir -p .tasks/{backlog,current,completed,templates}
mkdir -p .claude/{commands,output-styles,templates}
mkdir -p tools
echo "✅ Directories created"
echo ""

# 3. Copy GitHub integration module
echo "3️⃣ Installing GitHub integration module..."
if [ ! -d "$HOME/v6-tier1-template/tools/github_integration" ]; then
    echo "❌ Template not found at ~/v6-tier1-template/"
    echo "Please clone/copy the template first"
    exit 1
fi
cp -r "$HOME/v6-tier1-template/tools/github_integration" ./tools/
echo "✅ GitHub integration installed"
echo ""

# 4. Copy commands
echo "4️⃣ Installing commands..."
cp "$HOME/v6-tier1-template/.claude/commands/"*.md .claude/commands/
echo "✅ Commands installed"
echo ""

# 5. Copy templates
echo "5️⃣ Installing templates..."
cp "$HOME/v6-tier1-template/.tasks/templates/"*.j2 .tasks/templates/
echo "✅ Templates installed"
echo ""

# 6. Copy output styles
echo "6️⃣ Installing output styles..."
cp "$HOME/v6-tier1-template/.claude/output-styles/"*.md .claude/output-styles/
echo "✅ Output styles installed"
echo ""

# 7. Initialize GitHub labels (one-time per repo)
echo "7️⃣ Initializing GitHub labels..."
python3 << 'EOF'
import sys
sys.path.insert(0, './tools')

from github_integration.label_manager import get_label_taxonomy
from github_integration.gh_cli_wrapper import create_label

try:
    taxonomy = get_label_taxonomy()
    created = 0
    for category, labels in taxonomy.items():
        for label in labels:
            try:
                create_label(label.name, label.color, label.description)
                created += 1
            except Exception:
                pass  # Label might already exist
    print(f"✅ Initialized {created} labels")
except Exception as e:
    print(f"⚠️ Label initialization failed: {e}")
    print("You can run this manually later")
EOF
echo ""

# 8. Create example task
echo "8️⃣ Creating example task..."
cat > .tasks/backlog/EXAMPLE-001.task.md << 'EOF'
---
id: EXAMPLE-001
title: Example Task - Delete Me
type: feature
priority: low
status: backlog
created: 2025-10-18
area: general
---

# EXAMPLE-001: Example Task - Delete Me

## Problem Statement

This is an example task created during installation. You can delete this file.

## Acceptance Criteria

- [ ] Understand how tasks work
- [ ] Create your first real task
- [ ] Delete this example

## Implementation Notes

Try these commands:
- `/task-get EXAMPLE-001` - View this task
- `/task-list` - List all tasks
- `/task-create feature "My First Task"` - Create a new task
- `/spec-epic "My First Epic"` - Create an epic with spec
EOF
echo "✅ Example task created"
echo ""

# 9. Summary
echo "✨ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Try: /task-get EXAMPLE-001"
echo "2. Try: /task-list"
echo "3. Try: /task-create feature \"Your first task\""
echo "4. Try: /spec-epic \"Your first epic\""
echo ""
echo "📚 Documentation:"
echo "- Commands: .claude/commands/"
echo "- Templates: .tasks/templates/"
echo "- GitHub integration: tools/github_integration/README.md"
echo ""
echo "🎉 Happy tasking!"
```

**Day 2-4: Install in 3 Diverse Projects**

Test installation in:
1. **Small project** (~5k LOC, solo developer)
2. **Medium project** (~50k LOC, small team)
3. **Large project** (~200k LOC, email_management_system)

For each project:
- Run `./setup-tier1.sh`
- Create test task: `/task-create feature "Test task"`
- Create test epic: `/spec-epic "Test epic"`
- Verify GitHub sync works
- Document any issues or customizations needed

**Day 5: Refine Based on Feedback**

Common customizations to document:
- Custom task templates per project type
- Additional frontmatter fields
- Project-specific contract formats
- Domain-specific labels

**Deliverable Week 3:**
- Installation script tested in 3 projects
- Documentation of common customizations
- Tier 1 proven to work across diverse projects

---

## Complete File Listing

### Commands (5 files)

**`.claude/commands/task-create.md`**
- Bash-based ID generation
- Template rendering (sed/envsubst)
- File creation
- Optional GitHub issue creation

**`.claude/commands/task-get.md`**
- Find task file (bash find)
- Display with Read tool

**`.claude/commands/task-update.md`**
- Update frontmatter (sed)
- Move file between directories
- GitHub status sync (if metadata exists)

**`.claude/commands/task-list.md`**
- Find all tasks (bash find)
- Parse frontmatter (grep)
- Filter by status/type
- Format output

**`.claude/commands/spec-epic.md`**
- Interactive questioning (AskUserQuestion)
- Epic directory structure creation
- spec.md, architecture.md, task.md generation
- GitHub issue creation
- Contract definition (YAML in spec.md)

### Templates (3 files)

**`.tasks/templates/task.md.j2`**
- Task frontmatter structure
- Problem statement
- Acceptance criteria
- Progress checkboxes

**`.tasks/templates/spec.md.j2`**
- Epic frontmatter
- Problem statement
- User scenarios
- Functional requirements
- **Contract definitions (YAML blocks)**
- Technical constraints
- Success metrics

**`.tasks/templates/architecture.md.j2`**
- System overview
- Component descriptions
- Data flow diagrams
- Database schema
- API endpoints

### Output Styles (1 file)

**`.claude/output-styles/spec-architect.md`**
- Batched questioning behavior
- Zero-ambiguity tolerance
- Structured spec creation
- Clear artifact organization

### GitHub Integration (9 files)

**`tools/github_integration/README.md`**
- Complete documentation
- Usage examples
- Troubleshooting

**`tools/github_integration/GITHUB_CLI_USAGE.md`**
- gh CLI approach guide
- Zero-config setup
- Benefits over PyGithub

**`tools/github_integration/models.py`**
- `GitHubIssueMetadata` (Pydantic)
- `ProgressUpdate`
- `IssueSummary`
- `IssueLabel`

**`tools/github_integration/gh_cli_wrapper.py`**
- `create_issue()`
- `create_epic_issue()`
- `create_sub_issue()`
- `post_comment()`
- `sync_issue_status()`
- `create_label()`

**`tools/github_integration/issue_sync_gh.py`**
- `create_github_issue_from_epic()`
- `sync_status_to_github_simple()`
- `update_task_metadata()`
- `get_issue_metadata()`

**`tools/github_integration/issue_mapper.py`**
- `extract_issue_summary()`
- `format_issue_body()`
- `format_progress_comment()`

**`tools/github_integration/label_manager.py`**
- `get_label_taxonomy()` (24 labels)
- `get_labels_for_task()`
- `sync_labels_to_repo_gh()`

**`tools/github_integration/progress_reporter.py`**
- `post_progress_update()`
- `create_sub_issues_for_parallel_work()`

**`tools/github_integration/test_github_integration.py`**
- Unit tests for all modules

### Installation (1 file)

**`setup-tier1.sh`**
- Verify gh CLI authentication
- Create directory structure
- Copy all files
- Initialize GitHub labels
- Create example task

---

## Usage Examples

### Example 1: Create Simple Task

```bash
# Create task
/task-create feature "Add OAuth login"

# Output:
# ✅ Created task: FEATURE-003
# 📁 Location: .tasks/backlog/FEATURE-003.task.md
# 📋 Title: Add OAuth login
#
# Next steps:
# - Edit task file to add details
# - Run /task-get FEATURE-003 to view
# - Run /task-update FEATURE-003 current to start work
```

### Example 2: Create Epic with Spec

```bash
# Start epic creation
/spec-epic "Real-time Notifications"

# Claude asks questions (Round 1):
# Q1: What user pain point does this solve?
# Q2: What is the current manual workaround?
# Q3: What is the desired automated behavior?
# Q4: What is the expected impact?

# You answer questions

# Claude asks more questions (Round 2, 3)

# Claude creates:
# ✅ Epic created: EPIC-008
# 📁 Location: .tasks/backlog/EPIC-008-RealtimeNotifications
#
# Created files:
# - spec.md (WHAT/WHY - user scenarios, requirements, contracts)
# - architecture.md (HOW - system design, components)
# - task.md (workflow metadata)
# - contracts/ (contract definitions)
#
# 🔗 GitHub Issue: https://github.com/user/repo/issues/45
#
# Next steps:
# 1. Review and refine spec.md
# 2. Add implementation details
# 3. Start work: /task-update EPIC-008 current
```

### Example 3: Work on Task with GitHub Sync

```bash
# Start work on epic
/task-update EPIC-008 current

# Output:
# ✅ Updated EPIC-008: backlog → current
# 📁 New location: .tasks/current/EPIC-008-RealtimeNotifications/
# ✅ Synced status to GitHub: current
#
# GitHub: Status label updated (in-progress)
# GitHub: Comment posted "Status updated: backlog → in-progress"

# Implement the feature
# (Claude Code helps with implementation)

# Complete the epic
/task-update EPIC-008 completed

# Output:
# ✅ Updated EPIC-008: current → completed
# 📁 New location: .tasks/completed/EPIC-008-RealtimeNotifications/
# ✅ Synced status to GitHub: completed
#
# GitHub: Issue closed
# GitHub: Status label updated (completed)
```

### Example 4: List Tasks

```bash
# List all tasks
/task-list

# Output:
# 📋 Tasks:
#
# [backlog] EPIC-009 - User Dashboard Redesign (type: epic, priority: high)
# [backlog] FEATURE-004 - Add dark mode (type: feature, priority: medium)
# [current] EPIC-008 - Real-time Notifications (type: epic, priority: high)
# [current] BUG-002 - Fix mobile layout (type: bug, priority: critical)
# [completed] FEATURE-001 - OAuth login (type: feature, priority: high)
#
# Total: 5 tasks

# List only current tasks
/task-list current

# List only features
/task-list "" feature

# List current bugs
/task-list current bug
```

---

## Contract Definition in Tier 1 (No Generation)

### What Goes in spec.md

```markdown
## Data Contracts

### Authentication API

#### Login Request/Response
```yaml
endpoint: POST /api/auth/login

request:
  email: string           # User's email
  password: string        # Plain text (server hashes)
  remember_me: boolean    # Optional, default false

response_success:
  token: string          # JWT, expires 24h
  user_id: string        # UUID
  email: string
  name: string

response_error:
  error: string          # Error code (INVALID_CREDENTIALS, etc.)
  message: string        # Human-readable message
```

#### Token Refresh
```yaml
endpoint: POST /api/auth/refresh

request:
  refresh_token: string

response_success:
  token: string          # New JWT
  expires_at: datetime   # ISO 8601
```

### User Profile API

#### Get Profile
```yaml
endpoint: GET /api/users/{user_id}

response:
  user_id: string
  email: string
  name: string
  avatar_url: string     # Optional
  created_at: datetime
  roles: array<string>   # ["admin", "user"]
  preferences:
    theme: string        # "light" | "dark"
    language: string     # ISO 639-1 code
```

#### Update Profile
```yaml
endpoint: PUT /api/users/{user_id}

request:
  name: string           # Optional
  avatar_url: string     # Optional
  preferences: object    # Optional

response:
  # Same as Get Profile
```
```

### What This Achieves

✅ **Clear contract definition** - Everyone knows what data looks like
✅ **Human-readable** - Stakeholders can review during spec creation
✅ **Part of planning** - Defined as you create the spec
✅ **No tooling required** - Just YAML in markdown
✅ **Robust** - No fragile generation process

### What Tier 2 Adds (Optional)

Tier 2 would generate from these YAML definitions:

**`contracts/auth/login.schema.json`:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["email", "password"],
  "properties": {
    "email": {"type": "string"},
    "password": {"type": "string"},
    "remember_me": {"type": "boolean", "default": false}
  }
}
```

**`frontend/src/types/auth.ts`:**
```typescript
export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface LoginResponse {
  token: string;
  user_id: string;
  email: string;
  name: string;
}
```

**`backend/src/models/auth.py`:**
```python
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    token: str
    user_id: str
    email: str
    name: str
```

**But this is optional validation/testing, not core workflow.**

---

## Robustness Considerations

### What Makes Tier 1 Robust

✅ **No external services** - Just bash, files, and gh CLI
✅ **Non-blocking GitHub** - Sync failures don't stop work
✅ **Local source of truth** - .tasks/ files always authoritative
✅ **Simple operations** - ID generation, file moves, template rendering
✅ **No complex dependencies** - No MCP server, no PyGithub, no database
✅ **Transparent** - See exactly what bash commands run
✅ **Easy recovery** - Files are just markdown, can edit manually

### Failure Modes and Recovery

**GitHub sync fails:**
- Workflow continues (local files unaffected)
- Retry later via manual command
- Check logs: `tail tools/github_integration/*.log`

**Task file corrupted:**
- Edit manually (it's just markdown)
- Or delete and recreate with /task-create

**Directory structure wrong:**
- Re-run setup-tier1.sh
- Or create directories manually

**Template broken:**
- Edit .tasks/templates/*.j2
- Or copy from template repo

**No complex state to corrupt, no server to crash, no database to repair.**

---

## Comparison: Tier 1 vs Email System V6

| Feature | Tier 1 (Simplified) | Email System V6 (Full) |
|---------|---------------------|------------------------|
| **Task CRUD** | ✅ Bash commands | ✅ MCP server |
| **Epic Specs** | ✅ Interactive | ✅ Interactive + Validation |
| **GitHub Sync** | ✅ gh CLI (auto) | ✅ gh CLI (auto) |
| **Contract Definition** | ✅ YAML in spec.md | ✅ YAML in spec.md |
| **Contract Generation** | ❌ Tier 2 | ✅ JSON Schema + types |
| **Multi-Phase Workflow** | ❌ | ✅ Phases 0-7 |
| **Quality Gates** | ❌ | ✅ Build/lint loops |
| **Testing Infrastructure** | ❌ | ⚠️ (problematic) |
| **Graph-Server** | ❌ | ✅ |
| **Pattern Library** | ❌ | ✅ |
| **MCP Server** | ❌ | ✅ |
| **Setup Time** | 1-2 hours | 1 week |
| **Maintenance** | ~15 min/month | 4-8 hrs/month |
| **Lines of Code** | ~500 LOC | ~5000 LOC |
| **Fragility** | Very Low | Medium-High |
| **Best For** | **All projects** | >200k LOC only |

---

## Success Metrics

### Tier 1 is successful if:

✅ **Can create task in <30 seconds**
- `/task-create feature "Title"` → done

✅ **Can create complete epic spec in <20 minutes**
- `/spec-epic "Title"` → answer questions → done

✅ **GitHub sync works automatically**
- Task creation → GitHub issue created
- Status update → GitHub labels updated
- No manual intervention needed

✅ **Specs contain all info needed for implementation**
- Problem statement clear
- User scenarios complete
- Requirements testable
- Contracts defined (YAML)
- Architecture described

✅ **Zero maintenance required**
- Bash commands don't need updates
- GitHub integration stable
- Templates customized once

✅ **Works across diverse projects**
- Small projects (5k LOC)
- Medium projects (50k LOC)
- Large projects (200k LOC)

---

## Next Steps

### This Week
- [x] Finalize Tier 1 plan
- [ ] Extract github_integration from email_management_system
- [ ] Create template repository with all files
- [ ] Test installation in 1 project

### Next Week
- [ ] Refine based on testing
- [ ] Create setup-tier1.sh script
- [ ] Install in 2-3 more projects
- [ ] Document common customizations

### Week 3
- [ ] Rollout to all active projects
- [ ] Create user documentation
- [ ] Evaluate: is Tier 2 needed?

---

## Conclusion

Tier 1 provides **80% of the value** with **20% of the complexity**:

**What you get:**
- Complete task management (CRUD)
- Detailed epic specs with interactive creation
- GitHub integration for visibility
- Contract definition (human-readable YAML)
- Progress tracking via GitHub
- Professional appearance
- Zero configuration (gh CLI)

**What you skip:**
- MCP server (not needed for per-project work)
- JSON Schema generation (that's validation, Tier 2)
- Type compilation (that's testing, Tier 2)
- Multi-phase orchestration (overkill for most projects)
- Quality gates (causes more problems than it solves)

**Result:**
- 1-2 hour setup per project
- ~0 maintenance (bash + files)
- Robust (no fragile dependencies)
- Scalable (works for 1k to 200k LOC)
- Professional (GitHub visibility)

Start with Tier 1. Add Tier 2 only if contract validation proves valuable. Skip Tier 3 unless you're working on another email_management_system-scale project.

**The spec is the value. The automation is optional.**

---

**End of Plan**
