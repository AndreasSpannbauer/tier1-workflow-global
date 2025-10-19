# Phase 1C: Sequential Merge (After Parallel Implementation)

**Purpose**: Sequentially merge worktree branches back into the main branch in dependency order with conflict detection.

**Execution Context**: This phase only executes if `execution_mode = "parallel"` (after Phase 1B completes).

---

## Overview

After all parallel agents complete their work in isolated worktrees, Phase 1C merges their changes back into the main branch:

1. **Verify all agents succeeded** - Block merge if any domain failed
2. **Determine merge order** - Dependency-based ordering (database → backend → frontend → tests → docs)
3. **Sequential merge** - Merge one worktree at a time with conflict detection
4. **Handle conflicts** - Abort on conflicts, provide resolution guidance
5. **Verify success** - Check working directory state
6. **Cleanup worktrees** - Remove worktrees and branches after successful merge
7. **Create summary** - Write merge results to JSON

---

## Step 1: Verify All Agents Succeeded

**Before merging anything**, verify all domain implementations completed successfully:

```bash
echo ""
echo "🔗 Phase 1C: Sequential Merge"
echo ""

# Check if any domain failed
MERGE_VIABLE=1

for domain in $DOMAINS; do
  STATUS="${DOMAIN_STATUS[$domain]}"
  if [ "$STATUS" != "success" ]; then
    echo "❌ Cannot merge: ${domain} implementation failed (status: $STATUS)"
    MERGE_VIABLE=0
  fi
done

if [ $MERGE_VIABLE -eq 0 ]; then
  echo ""
  echo "⚠️ Merge blocked - one or more implementations failed"
  echo "   Review domain results:"
  for domain in $DOMAINS; do
    echo "     ${domain}: ${DOMAIN_STATUS[$domain]}"
  done
  echo ""
  echo "Manual intervention required."
  exit 1
fi

echo "✅ All domain implementations succeeded - proceeding with merge"
echo ""
```

**Key Points**:
- **Zero tolerance for failures** - Any failed domain blocks merge
- **Clear reporting** - Show which domains failed and their status
- **Exit early** - Don't attempt merge if any domain failed

---

## Step 2: Determine Merge Order (Dependency-Based)

**Strategy**: Merge in dependency order to minimize conflicts and ensure changes build on each other correctly.

**Standard dependency order**:
```
database → backend → frontend → tests → docs
```

**Rationale**:
- **Database first** - Schema changes needed by backend
- **Backend next** - API changes needed by frontend
- **Frontend next** - UI changes that consume backend APIs
- **Tests next** - Test both backend and frontend changes
- **Docs last** - Document all changes across layers

```bash
# Define dependency order for common domains
# database → backend → frontend → tests → docs

# Reorder domains based on dependencies
ORDERED_DOMAINS=()

if echo "$DOMAINS" | grep -q "database"; then
  ORDERED_DOMAINS+=("database")
fi

if echo "$DOMAINS" | grep -q "backend"; then
  ORDERED_DOMAINS+=("backend")
fi

if echo "$DOMAINS" | grep -q "frontend"; then
  ORDERED_DOMAINS+=("frontend")
fi

if echo "$DOMAINS" | grep -q "tests"; then
  ORDERED_DOMAINS+=("tests")
fi

if echo "$DOMAINS" | grep -q "docs"; then
  ORDERED_DOMAINS+=("docs")
fi

# Add any remaining domains not in standard order
for domain in $DOMAINS; do
  if [[ ! " ${ORDERED_DOMAINS[@]} " =~ " ${domain} " ]]; then
    ORDERED_DOMAINS+=("$domain")
  fi
done

echo "Merge order (dependency-based):"
for i in "${!ORDERED_DOMAINS[@]}"; do
  echo "  $((i+1)). ${ORDERED_DOMAINS[$i]}"
done
echo ""
```

**Custom ordering**:
- Projects can override standard order if needed
- Non-standard domains (e.g., "infrastructure", "config") appended at end
- Order preserved in merge summary for troubleshooting

---

## Step 3: Sequential Merge with Conflict Detection

**Strategy**: Merge one worktree at a time, detect conflicts immediately, abort on first conflict.

```bash
# Return to main repository directory
cd "$(git rev-parse --show-toplevel)"

MERGE_FAILED=0
MERGE_CONFLICTS=()

for domain in "${ORDERED_DOMAINS[@]}"; do
  WORKTREE_PATH="${WORKTREE_PATHS[$domain]}"

  echo "Merging: ${domain}"

  # Get branch name from worktree metadata
  BRANCH_NAME=$(python3 << EOF
import sys
sys.path.insert(0, "$HOME/tier1_workflow_global/implementation/worktree_manager")
from worktree_manager import get_worktree_metadata
import os

worktree_name = os.path.basename("${WORKTREE_PATH}")
metadata = get_worktree_metadata(worktree_name)
if metadata:
    print(metadata.branch_name)
else:
    print("")
    sys.exit(1)
EOF
)

  if [ -z "$BRANCH_NAME" ]; then
    echo "  ❌ Failed to get branch name from metadata"
    MERGE_CONFLICTS+=("${domain}")
    MERGE_FAILED=1
    continue
  fi

  echo "  Branch: ${BRANCH_NAME}"
  echo "  Merging into: $(git branch --show-current)"

  # Perform merge (no-fast-forward preserves branch history)
  git merge --no-ff "${BRANCH_NAME}" -m "Merge ${domain} implementation for ${ARGUMENTS}"

  # Check for conflicts
  if [ $? -ne 0 ]; then
    echo "  ❌ Merge conflict detected"
    MERGE_CONFLICTS+=("${domain}")
    MERGE_FAILED=1

    # Show conflicted files
    echo "  Conflicted files:"
    git diff --name-only --diff-filter=U | while read file; do
      echo "    - $file"
    done

    # Abort this merge
    git merge --abort

  else
    echo "  ✅ Merged successfully"
  fi

  echo ""
done
```

**Key Features**:
- **No-fast-forward merge** - Preserves branch history, easier to revert if needed
- **Immediate conflict detection** - Check git exit code after each merge
- **Conflict file listing** - Show which files have conflicts
- **Merge abort** - Clean abort on conflict, doesn't leave repository in merge state
- **Continue merging** - Attempt all merges even if one fails (to report all conflicts)

---

## Step 4: Handle Merge Conflicts

**Strategy**: Provide clear guidance for manual resolution, don't block workflow entirely.

```bash
if [ $MERGE_FAILED -eq 1 ]; then
  echo "⚠️ Merge conflicts detected in:"
  for domain in "${MERGE_CONFLICTS[@]}"; do
    echo "  - ${domain}"
  done
  echo ""
  echo "========================================="
  echo "MANUAL CONFLICT RESOLUTION REQUIRED"
  echo "========================================="
  echo ""
  echo "Steps to resolve:"
  echo "  1. Review conflicted domains above"
  echo "  2. Merge manually:"
  for domain in "${MERGE_CONFLICTS[@]}"; do
    WORKTREE_PATH="${WORKTREE_PATHS[$domain]}"
    BRANCH_NAME=$(python3 << EOF
import sys
sys.path.insert(0, "$HOME/tier1_workflow_global/implementation/worktree_manager")
from worktree_manager import get_worktree_metadata
import os

worktree_name = os.path.basename("${WORKTREE_PATH}")
metadata = get_worktree_metadata(worktree_name)
if metadata:
    print(metadata.branch_name)
EOF
)
    echo "     git merge ${BRANCH_NAME}"
    echo "     # Resolve conflicts in editor"
    echo "     git add ."
    echo "     git commit"
    echo ""
  done
  echo "  3. Run validation: npm run validate-all"
  echo "  4. Complete workflow: /execute-workflow ${ARGUMENTS} --resume"
  echo ""

  # Store conflict state
  mkdir -p ".workflow/outputs/${ARGUMENTS}"
  cat > ".workflow/outputs/${ARGUMENTS}/merge_conflicts.json" << EOF
{
  "status": "conflicts",
  "conflicted_domains": $(printf '%s\n' "${MERGE_CONFLICTS[@]}" | jq -R . | jq -s .),
  "resolution_required": true,
  "next_steps": [
    "Manually merge conflicted branches",
    "Resolve conflicts in editor",
    "Stage changes: git add .",
    "Commit: git commit",
    "Run validation: npm run validate-all",
    "Resume workflow: /execute-workflow ${ARGUMENTS} --resume"
  ],
  "conflict_timestamp": "$(date -Iseconds)"
}
EOF

  echo "Conflict state saved to: .workflow/outputs/${ARGUMENTS}/merge_conflicts.json"
  echo ""

  exit 1
fi
```

**Conflict Resolution Guidance**:
- **Clear instructions** - Step-by-step commands to resolve
- **Branch names** - Exact branches to merge manually
- **Validation reminder** - Ensure changes still pass validation
- **Resume mechanism** - Workflow can be resumed after resolution
- **Conflict state** - JSON record for troubleshooting

**Why not auto-resolve?**:
- Merge conflicts require human judgment
- Automatic resolution often makes wrong choices
- Manual resolution ensures correctness

---

## Step 5: Verify Merge Success

**After all merges complete**, verify the repository is in a clean state:

```bash
echo "✅ All merges completed successfully"
echo ""

# Check working directory is clean
if git diff --quiet && git diff --cached --quiet; then
  echo "✅ Working directory clean after merge"
else
  echo "⚠️ Working directory has uncommitted changes"
  echo "   This is unexpected - review changes:"
  git status --short
  echo ""
  echo "   If changes are expected, commit them manually."
fi

echo ""
```

**Why check for uncommitted changes?**:
- Merges should only integrate committed work from worktrees
- Uncommitted changes indicate something unexpected happened
- Alert user to review before proceeding

---

## Step 6: Cleanup Worktrees

**After successful merge**, remove worktrees and delete merged branches:

```bash
echo "🧹 Cleaning up worktrees..."

for domain in "${ORDERED_DOMAINS[@]}"; do
  WORKTREE_PATH="${WORKTREE_PATHS[$domain]}"
  WORKTREE_NAME=$(basename "${WORKTREE_PATH}")

  echo "  Removing: ${domain} (${WORKTREE_NAME})"

  python3 << EOF
import sys
sys.path.insert(0, "$HOME/tier1_workflow_global/implementation/worktree_manager")
from worktree_manager import cleanup_worktree

try:
    cleanup_worktree(
        worktree_name="${WORKTREE_NAME}",
        delete_branch=True  # Delete merged branch
    )
    print("    ✅ Removed")
except Exception as e:
    print(f"    ❌ Cleanup failed: {e}")
EOF

done

echo ""
echo "✅ Worktree cleanup complete"
```

**Cleanup actions**:
- **Remove worktree directory** - `git worktree remove <path>`
- **Delete merged branch** - Feature branch no longer needed after merge
- **Archive metadata** - Moved to `.worktrees/.metadata/archived/` for history
- **Error handling** - Report failures but don't block workflow

**Why delete branches?**:
- Merged branches clutter repository
- Changes are in main branch now
- Metadata archived for historical reference

---

## Step 7: Create Merge Summary

**Final step**: Write merge results to JSON for workflow tracking:

```bash
mkdir -p ".workflow/outputs/${ARGUMENTS}"

cat > ".workflow/outputs/${ARGUMENTS}/merge_summary.json" << EOF
{
  "status": "success",
  "execution_mode": "parallel",
  "merge_order": $(printf '%s\n' "${ORDERED_DOMAINS[@]}" | jq -R . | jq -s .),
  "merged_domains": $(printf '%s\n' "${ORDERED_DOMAINS[@]}" | jq -R . | jq -s .),
  "conflicts": [],
  "worktrees_cleaned": true,
  "completion_timestamp": "$(date -Iseconds)"
}
EOF

echo "✅ Phase 1C Complete: Sequential Merge"
echo "   Merge summary: .workflow/outputs/${ARGUMENTS}/merge_summary.json"
echo ""
```

**Summary includes**:
- **Status** - "success" or "conflicts"
- **Execution mode** - "parallel" (distinguishes from sequential)
- **Merge order** - Ordered list of domains merged
- **Merged domains** - List of successfully merged domains
- **Conflicts** - Empty if successful, list of domains if conflicts
- **Cleanup status** - Whether worktrees were cleaned up
- **Timestamp** - When merge completed

---

## Validation Checklist

Before completing Phase 1C, verify:

- [x] **All agents succeeded** - Verified before merge starts
- [x] **Merge order determined** - Dependency-based ordering applied
- [x] **Sequential merge implemented** - One worktree at a time
- [x] **Conflict detection** - Git exit code checked after each merge
- [x] **Merge abort on conflicts** - Clean abort without leaving merge state
- [x] **Conflict resolution guidance** - Clear steps provided
- [x] **Worktree cleanup** - Removed after successful merge
- [x] **Merge summary** - JSON written to `.workflow/outputs/`
- [x] **Clear status indicators** - User sees progress throughout

---

## Error Scenarios

### Scenario 1: Agent Failed (No Merge Attempted)

```
❌ Cannot merge: backend implementation failed (status: failed)

⚠️ Merge blocked - one or more implementations failed
   Review domain results:
     database: success
     backend: failed
     frontend: success

Manual intervention required.
```

**Resolution**: Fix implementation issues, re-run Phase 1B for failed domain.

---

### Scenario 2: Merge Conflict

```
Merging: frontend
  Branch: feature/TASK-001/frontend
  Merging into: main
  ❌ Merge conflict detected
  Conflicted files:
    - src/components/UserProfile.tsx
    - src/api/client.ts

⚠️ Merge conflicts detected in:
  - frontend

=========================================
MANUAL CONFLICT RESOLUTION REQUIRED
=========================================

Steps to resolve:
  1. Review conflicted domains above
  2. Merge manually:
     git merge feature/TASK-001/frontend
     # Resolve conflicts in editor
     git add .
     git commit

  3. Run validation: npm run validate-all
  4. Complete workflow: /execute-workflow TASK-001 --resume

Conflict state saved to: .workflow/outputs/TASK-001/merge_conflicts.json
```

**Resolution**:
1. Manually merge conflicted branch
2. Resolve conflicts in editor
3. Stage and commit
4. Run validation
5. Resume workflow

---

### Scenario 3: Uncommitted Changes After Merge

```
✅ All merges completed successfully

⚠️ Working directory has uncommitted changes
   This is unexpected - review changes:
 M src/config.py
?? temp_file.txt

   If changes are expected, commit them manually.
```

**Resolution**: Review changes, commit if expected, or discard if unintended.

---

## Integration with Workflow Orchestrator

**Orchestrator calls Phase 1C after Phase 1B completes**:

```bash
# In main workflow script (execute-workflow.md)

if [ "$EXECUTION_MODE" = "parallel" ]; then
  # Phase 1B: Parallel implementation (agents work in worktrees)
  source "$WORKFLOW_DIR/PHASE1B_PARALLEL_IMPLEMENTATION.sh"

  # Phase 1C: Sequential merge (this phase)
  source "$WORKFLOW_DIR/PHASE1C_SEQUENTIAL_MERGE.sh"

  # Check if merge succeeded
  if [ $? -ne 0 ]; then
    echo "❌ Merge failed - see conflict resolution guidance above"
    exit 1
  fi
else
  # Phase 1A: Sequential implementation (single agent, main branch)
  source "$WORKFLOW_DIR/PHASE1A_SEQUENTIAL_IMPLEMENTATION.sh"
fi

# Continue to Phase 2 (Validation)
source "$WORKFLOW_DIR/PHASE2_VALIDATION.sh"
```

---

## Benefits of Sequential Merge

**Why not merge in parallel?**

1. **Conflict detection** - Conflicts detected immediately, one at a time
2. **Dependency order** - Changes build on each other correctly
3. **Debugging** - Clear which merge caused issues
4. **Atomic operations** - Each merge is independent and reversible
5. **Simple coordination** - No complex merge orchestration needed

**Performance impact**:
- **Minimal** - Merges are fast (seconds per merge)
- **Parallelism already gained** - In Phase 1B implementation
- **Total time** - Dominated by agent work, not merge time

---

## Advanced: Merge Strategies

**Current strategy**: `--no-ff` (no fast-forward)

**Alternative strategies**:

```bash
# Fast-forward only (linear history)
git merge --ff-only "${BRANCH_NAME}"

# Squash merge (single commit)
git merge --squash "${BRANCH_NAME}"
git commit -m "Merge ${domain} implementation"

# Rebase merge (linear history, preserve commits)
git rebase "${BRANCH_NAME}"
```

**Recommendation**: Stick with `--no-ff` for Tier 1:
- Preserves branch history
- Easier to revert if needed
- Clear which commits came from which domain

---

## File Structure

```
.workflow/
└── outputs/
    └── TASK-001/
        ├── merge_summary.json          # Success summary
        └── merge_conflicts.json        # Conflict details (if conflicts)

.worktrees/
├── .metadata/
│   └── archived/                       # Archived worktree metadata
│       ├── TASK-001-backend-a3f2b1.json
│       ├── TASK-001-frontend-b4e1.json
│       └── TASK-001-database-c5d6e7.json
└── (worktree directories removed)
```

---

## Testing Phase 1C

**Test with mock worktrees**:

```bash
# Create test worktrees
python3 << EOF
import sys
sys.path.insert(0, "$HOME/tier1_workflow_global/implementation/worktree_manager")
from worktree_manager import create_worktree_for_agent

# Create 3 test worktrees
for domain in ["backend", "frontend", "database"]:
    metadata = create_worktree_for_agent("TEST-001", f"{domain} test")
    print(f"Created: {metadata.name}")
EOF

# Mark as completed (simulate agent success)
python3 << EOF
import sys
sys.path.insert(0, "$HOME/tier1_workflow_global/implementation/worktree_manager")
from worktree_manager import list_worktrees, update_worktree_status
from datetime import datetime

worktrees = list_worktrees(epic_id="TEST-001")
for wt in worktrees:
    update_worktree_status(wt.name, "completed", completed_at=datetime.utcnow())
    print(f"Marked completed: {wt.name}")
EOF

# Run Phase 1C merge
ARGUMENTS="TEST-001"
DOMAINS=("backend" "frontend" "database")
EXECUTION_MODE="parallel"

# ... (Phase 1C script here)

# Verify merge summary
cat ".workflow/outputs/TEST-001/merge_summary.json"
```

---

## Summary

Phase 1C (Sequential Merge) provides:

- ✅ **Safe merging** - Verify all agents succeeded before merging
- ✅ **Dependency-aware** - Merge in correct order (database → backend → frontend)
- ✅ **Conflict detection** - Immediate detection and abort on conflicts
- ✅ **Clear guidance** - Step-by-step resolution instructions
- ✅ **Automated cleanup** - Remove worktrees and branches after merge
- ✅ **Structured output** - JSON summary for workflow tracking

**Next Phase**: Phase 2 (Validation) - Run build/lint/tests on merged code.

---

## Related Documentation

- **Worktree Manager**: `~/tier1_workflow_global/implementation/worktree_manager/README.md`
- **Usage Examples**: `~/tier1_workflow_global/implementation/worktree_manager/USAGE_EXAMPLE.md`
- **Phase 1B (Parallel)**: `~/tier1_workflow_global/implementation/PHASE1B_PARALLEL_IMPLEMENTATION.md`
- **Assessment**: `~/tier1_workflow_global/docs/assessment/tier1_enhancement_assessment.md`
