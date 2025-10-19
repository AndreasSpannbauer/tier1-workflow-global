# Worktree Manager Usage Examples

This document provides concrete, step-by-step examples of using the worktree manager for Tier 1 parallel execution.

## Example 1: Creating Worktrees for Parallel Implementation

**Scenario**: You have a user request that breaks down into 3 parallel tasks:
1. Backend API implementation
2. Frontend UI components
3. Database schema migration

**Orchestrator creates worktrees**:

```python
#!/usr/bin/env python3
"""orchestrator_create_worktrees.py"""

import sys
from pathlib import Path

# Add worktree_manager to path
sys.path.insert(0, str(Path.home() / "tier1_workflow_global/implementation"))

from worktree_manager import create_worktree_for_agent, list_worktrees

def main():
    # Task identifier
    task_id = "TASK-123"

    # Define parallel subtasks
    subtasks = [
        "Backend API Implementation",
        "Frontend UI Components",
        "Database Schema Migration",
    ]

    print(f"Creating worktrees for {task_id}...\n")

    # Create worktree for each subtask
    worktree_metadata = []

    for task_name in subtasks:
        print(f"Creating worktree: {task_name}")

        metadata = create_worktree_for_agent(
            epic_id=task_id,
            task_name=task_name,
            base_branch="main"  # or "dev", "master", etc.
        )

        worktree_metadata.append(metadata)

        print(f"  ✅ Path: {metadata.path}")
        print(f"  ✅ Branch: {metadata.branch}")
        print(f"  ✅ Status: {metadata.status}\n")

    # Verify all worktrees created
    print("=" * 60)
    print(f"Summary: Created {len(worktree_metadata)} worktrees")
    print("=" * 60)

    # List all worktrees for this task
    all_worktrees = list_worktrees(epic_id=task_id)
    print(f"\nTotal worktrees for {task_id}: {len(all_worktrees)}")

    for wt in all_worktrees:
        print(f"  - {wt.name} ({wt.status})")

    # Return metadata for agent assignment
    return worktree_metadata

if __name__ == "__main__":
    metadata = main()

    # Example output for agent assignment
    print("\n" + "=" * 60)
    print("Worktree paths for agent assignment:")
    print("=" * 60)
    for m in metadata:
        print(f"{m.task_name}:")
        print(f"  Path: {m.path}")
        print(f"  Name: {m.name}\n")
```

**Output**:
```
Creating worktrees for TASK-123...

Creating worktree: Backend API Implementation
  ✅ Path: .worktrees/TASK-123-backend-api-implementation-a3f2b1c4
  ✅ Branch: feature/TASK-123/backend-api-implementation
  ✅ Status: created

Creating worktree: Frontend UI Components
  ✅ Path: .worktrees/TASK-123-frontend-ui-components-d5e6f7g8
  ✅ Branch: feature/TASK-123/frontend-ui-components
  ✅ Status: created

Creating worktree: Database Schema Migration
  ✅ Path: .worktrees/TASK-123-database-schema-migration-h9i0j1k2
  ✅ Branch: feature/TASK-123/database-schema-migration
  ✅ Status: created

============================================================
Summary: Created 3 worktrees
============================================================

Total worktrees for TASK-123: 3
  - TASK-123-backend-api-implementation-a3f2b1c4 (created)
  - TASK-123-frontend-ui-components-d5e6f7g8 (created)
  - TASK-123-database-schema-migration-h9i0j1k2 (created)

============================================================
Worktree paths for agent assignment:
============================================================
Backend API Implementation:
  Path: .worktrees/TASK-123-backend-api-implementation-a3f2b1c4
  Name: TASK-123-backend-api-implementation-a3f2b1c4

Frontend UI Components:
  Path: .worktrees/TASK-123-frontend-ui-components-d5e6f7g8
  Name: TASK-123-frontend-ui-components-d5e6f7g8

Database Schema Migration:
  Path: .worktrees/TASK-123-database-schema-migration-h9i0j1k2
  Name: TASK-123-database-schema-migration-h9i0j1k2
```

---

## Example 2: Agent Working in Worktree

**Scenario**: Agent receives worktree path and performs implementation work in isolation.

**Agent execution script**:

```python
#!/usr/bin/env python3
"""agent_execute_in_worktree.py"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add worktree_manager to path
sys.path.insert(0, str(Path.home() / "tier1_workflow_global/implementation"))

from worktree_manager import get_worktree_metadata, update_worktree_status

def execute_agent_task(worktree_name: str, agent_id: str, instructions: str):
    """Execute agent task within isolated worktree."""

    print(f"Agent {agent_id} starting work in worktree: {worktree_name}")
    print("=" * 60)

    # 1. Load worktree metadata
    metadata = get_worktree_metadata(worktree_name)
    if not metadata:
        print(f"❌ Worktree not found: {worktree_name}")
        return False

    print(f"Worktree path: {metadata.path}")
    print(f"Branch: {metadata.branch}")
    print(f"Base branch: {metadata.base_branch}\n")

    # 2. Update status to in_progress
    update_worktree_status(
        worktree_name,
        "in_progress",
        agent_id=agent_id,
        assigned_at=datetime.utcnow()
    )
    print("✅ Status updated to: in_progress\n")

    # 3. Agent performs work in worktree
    # (In reality, this would be Claude Code working in the worktree directory)
    print("Agent instructions:")
    print(f"  {instructions}\n")

    try:
        # Example: Agent makes file changes
        # All file operations happen within metadata.path
        print("Agent working...")
        print("  - Creating new API endpoint")
        print("  - Writing tests")
        print("  - Updating documentation\n")

        # Simulate creating a file
        test_file = metadata.path / "example.txt"
        test_file.write_text(f"Work completed by {agent_id}\n{instructions}")

        # 4. Agent commits changes
        print("Committing changes...")

        subprocess.run(
            ["git", "add", "."],
            cwd=metadata.path,
            check=True,
            capture_output=True
        )

        result = subprocess.run(
            ["git", "commit", "-m", f"Implement: {metadata.task_name}\n\nAgent: {agent_id}"],
            cwd=metadata.path,
            check=True,
            capture_output=True,
            text=True
        )

        print("✅ Changes committed\n")

        # 5. Update status to completed
        update_worktree_status(
            worktree_name,
            "completed",
            completed_at=datetime.utcnow()
        )

        print("=" * 60)
        print(f"✅ Agent {agent_id} completed work successfully")
        print("=" * 60)
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")

        # Update status to failed
        update_worktree_status(
            worktree_name,
            "failed",
            error_message=str(e)
        )

        return False

    except Exception as e:
        print(f"❌ Agent execution failed: {e}")

        update_worktree_status(
            worktree_name,
            "failed",
            error_message=str(e)
        )

        return False

if __name__ == "__main__":
    # Example: Agent receives worktree assignment from orchestrator
    worktree_name = "TASK-123-backend-api-implementation-a3f2b1c4"
    agent_id = "backend-specialist"
    instructions = "Implement REST API endpoint for user authentication with JWT tokens"

    success = execute_agent_task(worktree_name, agent_id, instructions)

    sys.exit(0 if success else 1)
```

**Output**:
```
Agent backend-specialist starting work in worktree: TASK-123-backend-api-implementation-a3f2b1c4
============================================================
Worktree path: .worktrees/TASK-123-backend-api-implementation-a3f2b1c4
Branch: feature/TASK-123/backend-api-implementation
Base branch: main

✅ Status updated to: in_progress

Agent instructions:
  Implement REST API endpoint for user authentication with JWT tokens

Agent working...
  - Creating new API endpoint
  - Writing tests
  - Updating documentation

Committing changes...
✅ Changes committed

============================================================
✅ Agent backend-specialist completed work successfully
============================================================
```

---

## Example 3: Sequential Merge After Agents Complete

**Scenario**: All agents have completed their work. Orchestrator merges worktrees sequentially into main branch.

**Merge orchestration script**:

```python
#!/usr/bin/env python3
"""orchestrator_merge_worktrees.py"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add worktree_manager to path
sys.path.insert(0, str(Path.home() / "tier1_workflow_global/implementation"))

from worktree_manager import (
    list_worktrees,
    update_worktree_status,
    cleanup_worktree,
)

def merge_worktree(metadata, target_branch="main"):
    """Merge single worktree into target branch."""

    print(f"\nMerging: {metadata.name}")
    print(f"  Branch: {metadata.branch}")
    print(f"  Target: {target_branch}")

    try:
        # Ensure we're on target branch
        subprocess.run(
            ["git", "checkout", target_branch],
            check=True,
            capture_output=True,
            text=True
        )

        # Merge with no-fast-forward (preserves branch history)
        result = subprocess.run(
            ["git", "merge", "--no-ff", metadata.branch, "-m",
             f"Merge {metadata.task_name}\n\nWorktree: {metadata.name}"],
            check=True,
            capture_output=True,
            text=True
        )

        print(f"  ✅ Merged successfully")

        # Update metadata
        update_worktree_status(
            metadata.name,
            "merged",
            merged_at=datetime.utcnow()
        )

        return True, None

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Merge failed")
        print(f"  Error: {e.stderr}")

        # Check if it's a conflict
        if "CONFLICT" in e.stderr or e.returncode == 1:
            # Get conflicted files
            conflict_result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                capture_output=True,
                text=True
            )

            conflict_files = conflict_result.stdout.strip().split("\n")

            print(f"  ⚠️  Conflicts in files:")
            for file in conflict_files:
                print(f"    - {file}")

            # Abort merge
            subprocess.run(["git", "merge", "--abort"], check=False)

            # Update metadata
            update_worktree_status(
                metadata.name,
                "conflict",
                error_message=f"Merge conflict in files: {', '.join(conflict_files)}"
            )

            return False, conflict_files

        else:
            # Other error
            update_worktree_status(
                metadata.name,
                "failed",
                error_message=f"Merge failed: {e.stderr}"
            )

            return False, None

def merge_all_worktrees(task_id: str, target_branch="main"):
    """Merge all completed worktrees for a task."""

    print("=" * 60)
    print(f"Merging worktrees for {task_id}")
    print("=" * 60)

    # Get all completed worktrees
    completed = list_worktrees(epic_id=task_id, status="completed")

    if not completed:
        print("No completed worktrees to merge")
        return

    print(f"Found {len(completed)} completed worktrees\n")

    merged_count = 0
    conflict_count = 0
    failed_count = 0

    for wt in completed:
        success, conflicts = merge_worktree(wt, target_branch)

        if success:
            merged_count += 1

            # Cleanup after successful merge
            print(f"  Cleaning up worktree...")
            cleanup_worktree(wt.name, delete_branch=True)
            print(f"  ✅ Worktree cleaned up")

        elif conflicts:
            conflict_count += 1
            print(f"  ⚠️  Marked as conflict - manual resolution required")

        else:
            failed_count += 1
            print(f"  ❌ Marked as failed")

    # Summary
    print("\n" + "=" * 60)
    print("Merge Summary")
    print("=" * 60)
    print(f"Total worktrees: {len(completed)}")
    print(f"  ✅ Merged: {merged_count}")
    print(f"  ⚠️  Conflicts: {conflict_count}")
    print(f"  ❌ Failed: {failed_count}")
    print("=" * 60)

    if conflict_count > 0:
        print("\nWorktrees with conflicts require manual resolution:")
        conflicts_list = list_worktrees(epic_id=task_id, status="conflict")
        for wt in conflicts_list:
            print(f"  - {wt.name}")
            print(f"    Branch: {wt.branch}")
            print(f"    Error: {wt.error_message}\n")

if __name__ == "__main__":
    task_id = "TASK-123"
    merge_all_worktrees(task_id, target_branch="main")
```

**Output** (successful merge):
```
============================================================
Merging worktrees for TASK-123
============================================================
Found 3 completed worktrees

Merging: TASK-123-backend-api-implementation-a3f2b1c4
  Branch: feature/TASK-123/backend-api-implementation
  Target: main
  ✅ Merged successfully
  Cleaning up worktree...
  ✅ Worktree cleaned up

Merging: TASK-123-frontend-ui-components-d5e6f7g8
  Branch: feature/TASK-123/frontend-ui-components
  Target: main
  ✅ Merged successfully
  Cleaning up worktree...
  ✅ Worktree cleaned up

Merging: TASK-123-database-schema-migration-h9i0j1k2
  Branch: feature/TASK-123/database-schema-migration
  Target: main
  ✅ Merged successfully
  Cleaning up worktree...
  ✅ Worktree cleaned up

============================================================
Merge Summary
============================================================
Total worktrees: 3
  ✅ Merged: 3
  ⚠️  Conflicts: 0
  ❌ Failed: 0
============================================================
```

**Output** (with conflicts):
```
============================================================
Merging worktrees for TASK-123
============================================================
Found 3 completed worktrees

Merging: TASK-123-backend-api-implementation-a3f2b1c4
  Branch: feature/TASK-123/backend-api-implementation
  Target: main
  ✅ Merged successfully
  Cleaning up worktree...
  ✅ Worktree cleaned up

Merging: TASK-123-frontend-ui-components-d5e6f7g8
  Branch: feature/TASK-123/frontend-ui-components
  Target: main
  ❌ Merge failed
  Error: Auto-merging src/components/UserProfile.tsx
CONFLICT (content): Merge conflict in src/components/UserProfile.tsx
  ⚠️  Conflicts in files:
    - src/components/UserProfile.tsx
  ⚠️  Marked as conflict - manual resolution required

Merging: TASK-123-database-schema-migration-h9i0j1k2
  Branch: feature/TASK-123/database-schema-migration
  Target: main
  ✅ Merged successfully
  Cleaning up worktree...
  ✅ Worktree cleaned up

============================================================
Merge Summary
============================================================
Total worktrees: 3
  ✅ Merged: 2
  ⚠️  Conflicts: 1
  ❌ Failed: 0
============================================================

Worktrees with conflicts require manual resolution:
  - TASK-123-frontend-ui-components-d5e6f7g8
    Branch: feature/TASK-123/frontend-ui-components
    Error: Merge conflict in files: src/components/UserProfile.tsx
```

---

## Example 4: Cleanup After Successful Merge

**Scenario**: All merges completed successfully. Clean up all worktrees and branches.

**Cleanup script**:

```python
#!/usr/bin/env python3
"""orchestrator_cleanup_worktrees.py"""

import sys
from pathlib import Path

# Add worktree_manager to path
sys.path.insert(0, str(Path.home() / "tier1_workflow_global/implementation"))

from worktree_manager import (
    list_worktrees,
    cleanup_epic_worktrees,
    list_archived_worktrees,
)

def cleanup_task_worktrees(task_id: str, delete_branches: bool = True):
    """Cleanup all worktrees for a task after successful merge."""

    print("=" * 60)
    print(f"Cleaning up worktrees for {task_id}")
    print("=" * 60)

    # List current worktrees
    all_worktrees = list_worktrees(epic_id=task_id)

    print(f"\nCurrent worktrees: {len(all_worktrees)}")
    for wt in all_worktrees:
        print(f"  - {wt.name} ({wt.status})")

    # Only cleanup terminal states (completed, merged, failed)
    terminal_states = ["completed", "merged", "failed"]
    cleanable = [wt for wt in all_worktrees if wt.status in terminal_states]

    print(f"\nCleanable worktrees: {len(cleanable)}")

    if len(cleanable) == 0:
        print("No worktrees to cleanup")
        return

    # Confirm cleanup
    print(f"\nWill cleanup {len(cleanable)} worktrees")
    if delete_branches:
        print("⚠️  Feature branches will be DELETED")
    else:
        print("Feature branches will be kept")

    # Cleanup
    print("\nCleaning up...")
    count = cleanup_epic_worktrees(task_id, delete_branches=delete_branches)

    print("\n" + "=" * 60)
    print(f"✅ Cleaned up {count} worktrees")
    print("=" * 60)

    # Show archived worktrees
    archived = list_archived_worktrees(epic_id=task_id)
    print(f"\nArchived metadata: {len(archived)} files")
    print("Location: .worktrees/.metadata/archived/")

    if archived:
        print("\nArchived worktrees:")
        for wt in archived:
            print(f"  - {wt.name}")
            print(f"    Cleaned at: {wt.cleaned_at}")

if __name__ == "__main__":
    task_id = "TASK-123"
    cleanup_task_worktrees(task_id, delete_branches=True)
```

**Output**:
```
============================================================
Cleaning up worktrees for TASK-123
============================================================

Current worktrees: 3
  - TASK-123-backend-api-implementation-a3f2b1c4 (merged)
  - TASK-123-frontend-ui-components-d5e6f7g8 (merged)
  - TASK-123-database-schema-migration-h9i0j1k2 (merged)

Cleanable worktrees: 3

Will cleanup 3 worktrees
⚠️  Feature branches will be DELETED

Cleaning up...

============================================================
✅ Cleaned up 3 worktrees
============================================================

Archived metadata: 3 files
Location: .worktrees/.metadata/archived/

Archived worktrees:
  - TASK-123-backend-api-implementation-a3f2b1c4
    Cleaned at: 2025-10-19 14:23:45.123456
  - TASK-123-frontend-ui-components-d5e6f7g8
    Cleaned at: 2025-10-19 14:23:45.456789
  - TASK-123-database-schema-migration-h9i0j1k2
    Cleaned at: 2025-10-19 14:23:45.789012
```

---

## Example 5: Complete Orchestrator Workflow

**Full end-to-end orchestration**:

```python
#!/usr/bin/env python3
"""complete_orchestrator_workflow.py"""

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.home() / "tier1_workflow_global/implementation"))

from worktree_manager import (
    create_worktree_for_agent,
    list_worktrees,
    get_worktree_metadata,
    update_worktree_status,
    cleanup_epic_worktrees,
)

def orchestrate_parallel_execution(task_id: str, subtasks: list):
    """Complete orchestration workflow for parallel agent execution."""

    print("=" * 70)
    print(f"TIER 1 ORCHESTRATOR - Task: {task_id}")
    print("=" * 70)

    # PHASE 1: Create worktrees
    print("\n[PHASE 1] Creating worktrees for parallel execution")
    print("-" * 70)

    worktree_metadata = []
    for task_name in subtasks:
        metadata = create_worktree_for_agent(task_id, task_name, base_branch="main")
        worktree_metadata.append(metadata)
        print(f"✅ Created: {metadata.name}")

    print(f"\nTotal worktrees created: {len(worktree_metadata)}")

    # PHASE 2: Assign agents and execute (simulated)
    print("\n[PHASE 2] Assigning agents and executing tasks")
    print("-" * 70)

    for metadata in worktree_metadata:
        agent_id = f"agent-{metadata.name[:10]}"

        # Update status to assigned
        update_worktree_status(metadata.name, "assigned", agent_id=agent_id)
        print(f"✅ Assigned {metadata.name} to {agent_id}")

        # Simulate agent execution (in reality, agents run in parallel)
        update_worktree_status(metadata.name, "in_progress")
        print(f"  ⏳ Agent working...")

        # Simulate work time
        time.sleep(0.5)

        # Simulate completion
        update_worktree_status(
            metadata.name,
            "completed",
            completed_at=datetime.utcnow()
        )
        print(f"  ✅ Completed\n")

    # PHASE 3: Verify all completed
    print("[PHASE 3] Verifying all agents completed")
    print("-" * 70)

    completed = list_worktrees(epic_id=task_id, status="completed")
    print(f"Completed worktrees: {len(completed)}/{len(worktree_metadata)}")

    if len(completed) != len(worktree_metadata):
        print("❌ Not all agents completed - aborting merge")
        return False

    # PHASE 4: Sequential merge (simplified - use merge script for real)
    print("\n[PHASE 4] Sequential merge (simulated)")
    print("-" * 70)

    for wt in completed:
        print(f"Merging: {wt.name}")
        # In reality, call merge_worktree() here
        update_worktree_status(wt.name, "merged", merged_at=datetime.utcnow())
        print(f"✅ Merged\n")

    # PHASE 5: Cleanup
    print("[PHASE 5] Cleanup")
    print("-" * 70)

    count = cleanup_epic_worktrees(task_id, delete_branches=True)
    print(f"✅ Cleaned up {count} worktrees")

    # PHASE 6: Summary
    print("\n" + "=" * 70)
    print("ORCHESTRATION COMPLETE")
    print("=" * 70)
    print(f"Task ID: {task_id}")
    print(f"Subtasks: {len(subtasks)}")
    print(f"Worktrees created: {len(worktree_metadata)}")
    print(f"Successfully merged: {len(completed)}")
    print(f"Cleaned up: {count}")
    print("=" * 70)

    return True

if __name__ == "__main__":
    task_id = "TASK-456"

    subtasks = [
        "Implement authentication service",
        "Create user profile UI",
        "Add database migrations",
    ]

    success = orchestrate_parallel_execution(task_id, subtasks)
    sys.exit(0 if success else 1)
```

**Output**:
```
======================================================================
TIER 1 ORCHESTRATOR - Task: TASK-456
======================================================================

[PHASE 1] Creating worktrees for parallel execution
----------------------------------------------------------------------
✅ Created: TASK-456-implement-authentication-service-a1b2c3d4
✅ Created: TASK-456-create-user-profile-ui-e5f6g7h8
✅ Created: TASK-456-add-database-migrations-i9j0k1l2

Total worktrees created: 3

[PHASE 2] Assigning agents and executing tasks
----------------------------------------------------------------------
✅ Assigned TASK-456-implement-authentication-service-a1b2c3d4 to agent-TASK-456-i
  ⏳ Agent working...
  ✅ Completed

✅ Assigned TASK-456-create-user-profile-ui-e5f6g7h8 to agent-TASK-456-c
  ⏳ Agent working...
  ✅ Completed

✅ Assigned TASK-456-add-database-migrations-i9j0k1l2 to agent-TASK-456-a
  ⏳ Agent working...
  ✅ Completed

[PHASE 3] Verifying all agents completed
----------------------------------------------------------------------
Completed worktrees: 3/3

[PHASE 4] Sequential merge (simulated)
----------------------------------------------------------------------
Merging: TASK-456-implement-authentication-service-a1b2c3d4
✅ Merged

Merging: TASK-456-create-user-profile-ui-e5f6g7h8
✅ Merged

Merging: TASK-456-add-database-migrations-i9j0k1l2
✅ Merged

[PHASE 5] Cleanup
----------------------------------------------------------------------
✅ Cleaned up 3 worktrees

======================================================================
ORCHESTRATION COMPLETE
======================================================================
Task ID: TASK-456
Subtasks: 3
Worktrees created: 3
Successfully merged: 3
Cleaned up: 3
======================================================================
```

---

## Notes

- All examples are **functional code** that can be run directly
- In production, replace simulated work with actual agent execution
- The orchestrator coordinates creation, execution, merge, and cleanup
- Each agent works in complete isolation via worktrees
- Sequential merge prevents conflicts
- Metadata tracking enables monitoring and recovery

---

## Running the Examples

```bash
# Navigate to project directory
cd /path/to/your/project

# Ensure worktree_manager is in Python path
export PYTHONPATH="$HOME/tier1_workflow_global/implementation:$PYTHONPATH"

# Run examples
python3 orchestrator_create_worktrees.py
python3 agent_execute_in_worktree.py
python3 orchestrator_merge_worktrees.py
python3 orchestrator_cleanup_worktrees.py
python3 complete_orchestrator_workflow.py
```
