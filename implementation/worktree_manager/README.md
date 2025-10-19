# Git Worktree Manager

**Purpose**: Enables parallel execution via git worktrees for Tier 1 workflow.

Git worktrees provide directory isolation, allowing multiple agents to work concurrently on separate feature branches without merge conflicts. Each agent gets its own workspace (worktree) on the filesystem, completely isolated from other agents.

## Architecture

### Core Components

1. **worktree_manager.py** - Core worktree operations
   - Create worktrees with automatic branch management
   - List and query worktrees
   - Update worktree metadata and status
   - Sanitize names for git compatibility

2. **models.py** - Pydantic data structures
   - `WorktreeMetadata` - Complete worktree lifecycle tracking
   - `MergeResult` - Result of merging single worktree
   - `MergeSummary` - Aggregate merge statistics
   - `WorktreeExecutionResult` - Agent task execution result

3. **cleanup.py** - Worktree removal and archival
   - Cleanup individual worktrees
   - Bulk cleanup for entire tasks
   - Archive metadata for historical tracking
   - Cleanup abandoned worktrees (age-based)

### Directory Structure

```
project_root/
└── .worktrees/                           # Root directory for all worktrees
    ├── TASK-001-api-a3f2b1/              # Worktree 1: API implementation
    │   └── (full project copy on feature branch)
    ├── TASK-001-frontend-b4c3d2/         # Worktree 2: Frontend implementation
    │   └── (full project copy on feature branch)
    └── .metadata/                        # Metadata tracking directory
        ├── TASK-001-api-a3f2b1.json      # Metadata for worktree 1
        ├── TASK-001-frontend-b4c3d2.json # Metadata for worktree 2
        └── archived/                     # Historical records
            └── TASK-001-api-a3f2b1-20251019-143000.json
```

## Core Functions

### Worktree Creation

```python
create_worktree_for_agent(
    epic_id: str,
    task_name: str,
    base_branch: str = "dev",
    project_root: Optional[Path] = None
) -> WorktreeMetadata
```

**Purpose**: Create isolated git worktree for agent execution.

**What it does**:
- Creates new git worktree in `.worktrees/{epic_id}-{sanitized_task_name}-{uuid}/`
- Creates feature branch: `feature/{epic_id}/{sanitized_task_name}`
- Generates and saves metadata to `.worktrees/.metadata/{worktree_name}.json`
- Returns `WorktreeMetadata` with path, branch, status="created"

**Example**:
```python
metadata = create_worktree_for_agent("TASK-001", "Backend API Implementation")
# Creates: .worktrees/TASK-001-backend-api-implementation-a3f2b1/
# Branch: feature/TASK-001/backend-api-implementation
# Metadata: .worktrees/.metadata/TASK-001-backend-api-implementation-a3f2b1.json
print(metadata.path)   # Path to worktree
print(metadata.branch) # Feature branch name
```

---

### List Worktrees

```python
list_worktrees(
    epic_id: Optional[str] = None,
    status: Optional[str] = None
) -> List[WorktreeMetadata]
```

**Purpose**: Query worktrees with optional filtering.

**What it does**:
- Reads all metadata files from `.worktrees/.metadata/`
- Applies filters for epic_id and status if provided
- Returns sorted list (most recent first)

**Example**:
```python
# List all worktrees
all_worktrees = list_worktrees()

# List worktrees for specific task
task_worktrees = list_worktrees(epic_id="TASK-001")

# List active worktrees
active = list_worktrees(status="in_progress")

# List completed worktrees for specific task
completed = list_worktrees(epic_id="TASK-001", status="completed")
```

---

### Get Worktree Metadata

```python
get_worktree_metadata(worktree_name: str) -> Optional[WorktreeMetadata]
```

**Purpose**: Load metadata for specific worktree.

**What it does**:
- Reads metadata file: `.worktrees/.metadata/{worktree_name}.json`
- Parses JSON and returns `WorktreeMetadata` object
- Returns `None` if not found

**Example**:
```python
metadata = get_worktree_metadata("TASK-001-api-a3f2b1")
if metadata:
    print(f"Status: {metadata.status}")
    print(f"Branch: {metadata.branch}")
    print(f"Created: {metadata.created_at}")
```

---

### Update Worktree Status

```python
update_worktree_status(
    worktree_name: str,
    status: str,
    error_message: Optional[str] = None,
    **kwargs
) -> None
```

**Purpose**: Update worktree lifecycle status.

**What it does**:
- Loads existing metadata
- Updates status field
- Saves updated metadata back to JSON file

**Valid statuses**:
- `created` - Worktree created, not yet assigned
- `assigned` - Assigned to agent, not started
- `in_progress` - Agent actively working
- `completed` - Agent finished successfully
- `failed` - Agent encountered error
- `merged` - Changes merged to base branch
- `cleaned` - Worktree removed and archived
- `conflict` - Merge conflict occurred

**Example**:
```python
# Mark worktree as in progress
update_worktree_status("TASK-001-api-a3f2b1", "in_progress")

# Mark as completed with timestamp
from datetime import datetime
update_worktree_status(
    "TASK-001-api-a3f2b1",
    "completed",
    completed_at=datetime.utcnow()
)

# Mark as failed with error
update_worktree_status(
    "TASK-001-api-a3f2b1",
    "failed",
    error_message="Tests failed: 3 errors"
)
```

---

### Cleanup Worktree

```python
cleanup_worktree(
    worktree_name: str,
    delete_branch: bool = False,
    force: bool = False
) -> None
```

**Purpose**: Remove worktree and optionally delete branch.

**What it does**:
- Validates worktree is in terminal state (completed/merged/failed)
- Runs `git worktree remove {path}`
- Optionally deletes feature branch
- Archives metadata to `.worktrees/.metadata/archived/`
- Removes active metadata file

**Example**:
```python
# Normal cleanup after successful merge
cleanup_worktree("TASK-001-api-a3f2b1", delete_branch=True)

# Force cleanup of failed worktree with uncommitted changes
cleanup_worktree("TASK-001-broken-a3f2b1", force=True, delete_branch=True)
```

---

### Cleanup Epic Worktrees

```python
cleanup_epic_worktrees(
    epic_id: str,
    delete_branches: bool = False
) -> int
```

**Purpose**: Bulk cleanup all worktrees for a task.

**What it does**:
- Lists all worktrees for `epic_id`
- Filters to terminal states (completed/merged/failed)
- Calls `cleanup_worktree()` for each
- Returns count of cleaned worktrees

**Example**:
```python
# Cleanup all completed worktrees for TASK-001
count = cleanup_epic_worktrees("TASK-001", delete_branches=True)
print(f"Cleaned up {count} worktrees")
```

---

## Tier 1 Usage Patterns

### Pattern 1: Orchestrator Creates Worktrees

The orchestrator creates multiple worktrees for parallel agent execution:

```python
from worktree_manager import create_worktree_for_agent, list_worktrees

# Orchestrator creates worktrees for parallel tasks
tasks = [
    ("TASK-001", "Backend API Implementation"),
    ("TASK-001", "Frontend UI Components"),
    ("TASK-001", "Database Schema Migration"),
]

worktree_metadata = []
for epic_id, task_name in tasks:
    metadata = create_worktree_for_agent(epic_id, task_name, base_branch="main")
    worktree_metadata.append(metadata)
    print(f"Created worktree: {metadata.path}")

# List all worktrees for this task
worktrees = list_worktrees(epic_id="TASK-001")
print(f"Total worktrees: {len(worktrees)}")
```

---

### Pattern 2: Agent Receives Worktree Path

Each agent receives its worktree path and works in isolation:

```python
from pathlib import Path
import subprocess

def agent_work_in_worktree(worktree_path: Path, task_description: str):
    """Agent performs work in isolated worktree."""

    # Change to worktree directory
    original_dir = Path.cwd()

    try:
        # All file operations happen in worktree
        # (e.g., via Claude Code working directory)

        # Agent makes changes, commits work
        subprocess.run(
            ["git", "add", "."],
            cwd=worktree_path,
            check=True
        )

        subprocess.run(
            ["git", "commit", "-m", f"Implement: {task_description}"],
            cwd=worktree_path,
            check=True
        )

        return True
    finally:
        # Return to original directory
        pass

# Example: Agent receives worktree_path from orchestrator
agent_work_in_worktree(
    Path(".worktrees/TASK-001-api-a3f2b1"),
    "Backend API Implementation"
)
```

---

### Pattern 3: Sequential Merge After Completion

Orchestrator merges worktrees sequentially after agents complete:

```python
import subprocess
from worktree_manager import list_worktrees, update_worktree_status, cleanup_worktree

def merge_worktree_sequential(worktree_metadata, target_branch="main"):
    """Merge single worktree into target branch."""

    try:
        # Switch to target branch
        subprocess.run(["git", "checkout", target_branch], check=True)

        # Merge feature branch
        result = subprocess.run(
            ["git", "merge", "--no-ff", worktree_metadata.branch],
            check=True,
            capture_output=True,
            text=True
        )

        # Update metadata
        update_worktree_status(worktree_metadata.name, "merged")
        print(f"✅ Merged: {worktree_metadata.branch}")
        return True

    except subprocess.CalledProcessError as e:
        # Handle merge conflict
        update_worktree_status(
            worktree_metadata.name,
            "conflict",
            error_message=f"Merge conflict: {e.stderr}"
        )
        print(f"❌ Conflict in: {worktree_metadata.branch}")
        return False

# Orchestrator merges all completed worktrees
completed_worktrees = list_worktrees(epic_id="TASK-001", status="completed")

for wt in completed_worktrees:
    success = merge_worktree_sequential(wt, target_branch="main")

    if success:
        # Cleanup after successful merge
        cleanup_worktree(wt.name, delete_branch=True)
```

---

### Pattern 4: Cleanup After Successful Merge

```python
from worktree_manager import cleanup_epic_worktrees

# After all merges complete, cleanup all worktrees
count = cleanup_epic_worktrees("TASK-001", delete_branches=True)
print(f"Cleaned up {count} worktrees")

# Metadata is archived to .worktrees/.metadata/archived/
# for historical tracking
```

---

## Dependencies

**Required**:
- Python 3.8+
- `pydantic` (data validation)
- `git` (command-line tool)

**Installation**:
```bash
pip install pydantic
```

---

## Git Worktree Basics

### What is a Git Worktree?

A git worktree is a complete, separate working directory linked to the same git repository. Each worktree:
- Has its own working directory on the filesystem
- Can have a different branch checked out
- Shares the same `.git` repository data (commits, objects)
- Allows parallel work without switching branches

### Advantages for Tier 1

1. **True parallelism**: Multiple agents work simultaneously without interference
2. **No branch switching**: Each agent has its own branch checked out
3. **File isolation**: Changes in one worktree don't affect others
4. **Fast creation**: Worktrees share git data, creation is instant
5. **Clean merges**: Sequential merge after parallel work prevents conflicts

### Git Commands Used

```bash
# Create worktree
git worktree add .worktrees/TASK-001-api-a3f2b1 -b feature/TASK-001/api main

# List worktrees
git worktree list

# Remove worktree
git worktree remove .worktrees/TASK-001-api-a3f2b1

# Prune stale worktrees
git worktree prune
```

---

## WorktreeMetadata Fields

```python
class WorktreeMetadata:
    # Identification
    name: str                  # "TASK-001-api-a3f2b1"
    epic_id: str               # "TASK-001"
    task_name: str             # "Backend API Implementation"

    # Git information
    path: Path                 # .worktrees/TASK-001-api-a3f2b1
    branch: str                # feature/TASK-001/api
    base_branch: str           # "main"

    # Agent assignment
    agent_id: Optional[str]    # "backend-specialist"

    # Lifecycle status
    status: Literal[...]       # created|assigned|in_progress|completed|failed|merged|cleaned|conflict

    # Timestamps
    created_at: datetime
    assigned_at: Optional[datetime]
    completed_at: Optional[datetime]
    merged_at: Optional[datetime]
    cleaned_at: Optional[datetime]

    # Execution tracking
    commits: List[str]         # Commit hashes
    error_message: Optional[str]

    # Integration
    github_sub_issue: Optional[int]
```

---

## Error Handling

### Worktree Creation Failure

```python
try:
    metadata = create_worktree_for_agent("TASK-001", "API")
except RuntimeError as e:
    # Git command failed (e.g., base branch doesn't exist)
    print(f"Worktree creation failed: {e}")
```

### Cleanup Failure

```python
from worktree_manager import cleanup_worktree

try:
    cleanup_worktree("TASK-001-api-a3f2b1", delete_branch=True)
except ValueError as e:
    # Worktree not in terminal state
    print(f"Cannot cleanup: {e}")
    # Use force=True if needed
    cleanup_worktree("TASK-001-api-a3f2b1", force=True, delete_branch=True)
```

### Merge Conflicts

Merge conflicts require manual resolution. The orchestrator should:
1. Detect conflict via git exit code
2. Mark worktree status as "conflict"
3. Store conflict details in metadata
4. Alert user for manual resolution
5. Continue merging other worktrees

---

## Best Practices

1. **Always use epic_id consistently**: Group related worktrees by task ID
2. **Update status frequently**: Keep metadata in sync with actual work
3. **Cleanup after merge**: Remove worktrees and branches to avoid clutter
4. **Handle conflicts gracefully**: Don't abort entire merge on single conflict
5. **Archive metadata**: Historical tracking helps debug issues
6. **Use meaningful task names**: They become part of branch names
7. **Monitor abandoned worktrees**: Run periodic cleanup of old worktrees

---

## Advanced Operations

### List All Git Worktrees

```python
from worktree_manager import get_all_git_worktrees

# Get worktrees directly from git (bypasses metadata)
worktrees = get_all_git_worktrees()
for wt in worktrees:
    print(f"{wt['path']} -> {wt['branch']}")
```

### Cleanup Abandoned Worktrees

```python
from worktree_manager import cleanup_abandoned_worktrees

# Cleanup worktrees older than 7 days in non-terminal state
count = cleanup_abandoned_worktrees(max_age_days=7)
print(f"Cleaned up {count} abandoned worktrees")
```

### List Archived Worktrees

```python
from worktree_manager import list_archived_worktrees

# View historical metadata
archived = list_archived_worktrees(epic_id="TASK-001")
for wt in archived:
    print(f"{wt.name} - Cleaned at: {wt.cleaned_at}")
```

---

## Troubleshooting

### Issue: Worktree directory exists but not in git

**Symptoms**: Directory exists but `git worktree list` doesn't show it

**Solution**:
```bash
# Prune stale worktree references
git worktree prune

# Manually remove directory
rm -rf .worktrees/TASK-001-api-a3f2b1

# Remove metadata file
rm .worktrees/.metadata/TASK-001-api-a3f2b1.json
```

### Issue: Cannot remove worktree with uncommitted changes

**Symptoms**: `git worktree remove` fails with error about uncommitted changes

**Solution**:
```python
# Force cleanup
cleanup_worktree("TASK-001-api-a3f2b1", force=True)
```

### Issue: Branch already exists

**Symptoms**: `create_worktree_for_agent` fails because feature branch exists

**Solution**:
```bash
# Delete existing branch
git branch -D feature/TASK-001/api

# Or use different task name to generate unique branch
metadata = create_worktree_for_agent("TASK-001", "API Implementation v2")
```

### Issue: Metadata out of sync with git

**Symptoms**: Metadata shows worktree exists but directory is gone

**Solution**:
```python
# Compare metadata with git
from worktree_manager import list_worktrees, get_all_git_worktrees

metadata_worktrees = list_worktrees()
git_worktrees = get_all_git_worktrees()

# Identify mismatches and cleanup stale metadata
```

---

## Integration with Tier 1 Orchestrator

The orchestrator should:

1. **Create worktrees** for parallel agent tasks
2. **Pass worktree path** to each agent via environment or argument
3. **Monitor agent progress** by checking worktree metadata status
4. **Merge sequentially** after all agents complete
5. **Handle conflicts** by marking status and alerting user
6. **Cleanup** after successful merge

**Example orchestrator workflow**:

```python
# 1. Create worktrees
worktrees = []
for task in parallel_tasks:
    metadata = create_worktree_for_agent(epic_id, task.name)
    update_worktree_status(metadata.name, "assigned", agent_id=task.agent_id)
    worktrees.append(metadata)

# 2. Execute agents in parallel (pass metadata.path to each agent)
# ... agent execution happens here ...

# 3. Wait for all agents to complete
# ... polling or callback mechanism ...

# 4. Sequential merge
for wt in worktrees:
    if merge_worktree_sequential(wt):
        cleanup_worktree(wt.name, delete_branch=True)

# 5. Final cleanup
cleanup_epic_worktrees(epic_id, delete_branches=True)
```

---

## Notes

- This is a **minimal implementation** adapted from email_management_system V6
- **Agent execution** and **merge coordination** modules are NOT included
- For full-featured worktree management with pre-merge validation, rollback, and conflict resolution, see the original implementation
- This version provides **core operations** sufficient for basic Tier 1 parallel execution

---

## Source

Adapted from: `/home/andreas-spannbauer/coding_projects/email_management_system/tools/worktree_manager/`

Original implementation includes:
- `agent_isolator.py` - Agent assignment and isolated execution
- `merge_coordinator.py` - Sequential merge with conflict detection
- `pre_merge_validator.py` - Validation before merge
- `rollback_manager.py` - Rollback on merge failure
- `test_worktree_manager.py` - Comprehensive test suite
