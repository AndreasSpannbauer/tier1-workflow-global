# Phase 1B: Parallel Implementation

**Execution Condition:** Only executes if `execution_mode = "parallel"` (from Phase 0)

**Purpose:** Deploy multiple agents in isolated git worktrees for parallel execution

**Dependencies:**
- Phase 0 completed with parallel plan generated
- Worktree manager available (`~/tier1_workflow_global/implementation/worktree_manager/`)
- Agent definitions and briefings configured

---

## Overview

Phase 1B implements true parallel execution using git worktrees. Each domain (backend, frontend, database) gets:
- Isolated worktree directory
- Dedicated feature branch
- Domain-specific agent with briefing
- Subset of files from parallel plan

**Workflow:**
1. Load parallel plan from Phase 0
2. Create isolated worktrees (orchestrator)
3. Deploy parallel agents (single message, multiple Task calls)
4. Wait for completion
5. Collect results from worktrees
6. Aggregate results

---

## Step 1: Load Parallel Plan

```bash
if [ "$EXECUTION_MODE" = "parallel" ]; then
  echo ""
  echo "🔀 Phase 1B: Parallel Implementation"
  echo "======================================================================"
  echo ""

  # Load parallel plan from Phase 0
  PARALLEL_PLAN_FILE=".workflow/outputs/${ARGUMENTS}/parallel_analysis.json"

  if [ ! -f "$PARALLEL_PLAN_FILE" ]; then
    echo "❌ Parallel plan not found: $PARALLEL_PLAN_FILE"
    echo "   Run Phase 0 again or switch to sequential mode"
    exit 1
  fi

  PARALLEL_PLAN=$(cat "$PARALLEL_PLAN_FILE")

  # Extract domain list
  DOMAINS=$(echo "$PARALLEL_PLAN" | jq -r '.parallel_plan | keys[]')

  if [ -z "$DOMAINS" ]; then
    echo "❌ No domains found in parallel plan"
    exit 1
  fi

  echo "Parallel execution across domains:"
  for domain in $DOMAINS; do
    file_count=$(echo "$PARALLEL_PLAN" | jq -r ".parallel_plan.\"$domain\".files | length")
    task_desc=$(echo "$PARALLEL_PLAN" | jq -r ".parallel_plan.\"$domain\".task_description" | head -c 60)
    echo "  - $domain: $file_count files"
    echo "    Task: $task_desc..."
  done
  echo ""
fi
```

**Outputs:**
- `DOMAINS` - Space-separated list of domains (backend, frontend, database, etc.)
- `PARALLEL_PLAN` - JSON object with domain-specific file lists and tasks

---

## Step 2: Create Worktrees (Orchestrator)

**Critical:** Orchestrator creates ALL worktrees BEFORE deploying agents.

```bash
echo "Creating isolated worktrees..."
echo "----------------------------------------------------------------------"

# Import worktree manager path
WORKTREE_MANAGER=~/tier1_workflow_global/implementation/worktree_manager

# Store worktree paths for agent deployment
declare -A WORKTREE_PATHS
declare -A WORKTREE_BRANCHES

# Get current branch as base
CURRENT_BRANCH=$(git branch --show-current)

for domain in $DOMAINS; do
  echo "  Creating worktree for: $domain"

  # Create worktree using Python script
  WORKTREE_INFO=$(python3 << EOF
import sys
sys.path.insert(0, "$WORKTREE_MANAGER")
from worktree_manager import create_worktree_for_agent
import json

try:
    metadata = create_worktree_for_agent(
        epic_id="${ARGUMENTS}",
        task_name="${domain}",
        base_branch="${CURRENT_BRANCH}"
    )

    print(json.dumps({
        "path": str(metadata.path),
        "branch": metadata.branch_name,
        "worktree_name": metadata.name
    }))
except Exception as e:
    print(json.dumps({"error": str(e)}), file=sys.stderr)
    sys.exit(1)
EOF
)

  # Check for errors
  if [ $? -ne 0 ]; then
    echo "    ❌ Failed to create worktree for $domain"
    echo "    Error: $WORKTREE_INFO"
    exit 1
  fi

  # Parse worktree info
  WORKTREE_PATH=$(echo "$WORKTREE_INFO" | jq -r '.path')
  WORKTREE_BRANCH=$(echo "$WORKTREE_INFO" | jq -r '.branch')
  WORKTREE_NAME=$(echo "$WORKTREE_INFO" | jq -r '.worktree_name')

  # Store for agent deployment
  WORKTREE_PATHS[$domain]="$WORKTREE_PATH"
  WORKTREE_BRANCHES[$domain]="$WORKTREE_BRANCH"

  echo "    ✅ Created: $WORKTREE_PATH"
  echo "    Branch: $WORKTREE_BRANCH"
done

echo ""
echo "✅ All worktrees created successfully"
echo ""
```

**Key Points:**
- Worktree manager handles branch creation and metadata tracking
- Absolute paths stored for agent assignment
- Each domain gets isolated directory: `.worktrees/EPIC-XXX-{domain}-{uuid}/`
- Feature branches: `feature/EPIC-XXX/{domain}`

---

## Step 3: Deploy Parallel Agents

**CRITICAL:** All Task() calls must be in a SINGLE message for parallel execution.

```markdown
echo "Deploying parallel agents..."
echo "----------------------------------------------------------------------"
echo ""
echo "⚠️  IMPORTANT: Agents will work in parallel. Do not interrupt."
echo ""

# Prepare agent deployment instructions
cat > /tmp/parallel_agent_deployment.txt << 'DEPLOYMENT_END'

I will now deploy PARALLEL AGENTS for each domain. Each agent receives:
- Isolated worktree directory (absolute path)
- Domain-specific file list from parallel plan
- Domain-specific briefing
- Epic specification and architecture

**CRITICAL INSTRUCTIONS FOR AGENTS:**
1. CD into worktree directory FIRST: `cd {worktree_path}`
2. ALL file operations must happen in the worktree
3. Follow prescriptive plan for domain-specific files only
4. Write results to `.workflow/outputs/{epic_id}/{domain}_results.json`
5. Report completion status (success/partial/failed)

---

DEPLOYMENT_END

# Deploy agents for each domain (ALL IN THIS SINGLE MESSAGE)
```

**For each domain, deploy agent with:**

```python
# BACKEND DOMAIN
Task(
    subagent_type="general-purpose",
    description="Backend implementation for ${ARGUMENTS}",
    prompt=f"""
YOU ARE: Implementation Agent V1

[Read ~/tier1_workflow_global/implementation/agent_definitions/implementation_agent_v1.md]

DOMAIN BRIEFING:

[Read ~/tier1_workflow_global/implementation/agent_briefings/backend_implementation.md]

PROJECT ARCHITECTURE:

[Read ~/tier1_workflow_global/implementation/agent_briefings/project_architecture.md]

WORKTREE DIRECTORY: ${WORKTREE_PATHS[backend]}

CRITICAL: Change to worktree directory FIRST:
```bash
cd ${WORKTREE_PATHS[backend]}
```

ALL file operations must happen in this directory. You are working in ISOLATION.

EPIC SPECIFICATION:

[Read ${EPIC_DIR}/spec.md]

ARCHITECTURE:

[Read ${EPIC_DIR}/architecture.md]

PRESCRIPTIVE PLAN (backend domain only):

$(echo "$PARALLEL_PLAN" | jq -r '.parallel_plan.backend.task_description')

FILES TO CREATE/MODIFY (backend domain):

$(echo "$PARALLEL_PLAN" | jq -r '.parallel_plan.backend.files[]')

EXECUTION INSTRUCTIONS:

1. CD into worktree: `cd ${WORKTREE_PATHS[backend]}`
2. Verify you're in correct directory: `pwd`
3. Follow prescriptive plan for backend files only
4. Create/modify files as specified
5. Add error handling
6. Validate syntax (Python: `python -m py_compile`, TypeScript: `tsc --noEmit`)
7. Write results JSON

OUTPUT FILE:
${WORKTREE_PATHS[backend]}/.workflow/outputs/${ARGUMENTS}/backend_results.json

Format:
{{
  "status": "success|partial|failed",
  "epic_id": "${ARGUMENTS}",
  "domain": "backend",
  "worktree_path": "${WORKTREE_PATHS[backend]}",
  "files_created": [...],
  "files_modified": [...],
  "issues_encountered": [...],
  "completion_timestamp": "2025-10-19T14:30:00Z"
}}

BEGIN IMPLEMENTATION.
"""
)

# FRONTEND DOMAIN (if exists)
$(if echo "$DOMAINS" | grep -q "frontend"; then
echo 'Task(
    subagent_type="general-purpose",
    description="Frontend implementation for ${ARGUMENTS}",
    prompt=f"""
YOU ARE: Implementation Agent V1

[Read ~/tier1_workflow_global/implementation/agent_definitions/implementation_agent_v1.md]

DOMAIN BRIEFING:

[Read ~/tier1_workflow_global/implementation/agent_briefings/frontend_implementation.md]

PROJECT ARCHITECTURE:

[Read ~/tier1_workflow_global/implementation/agent_briefings/project_architecture.md]

WORKTREE DIRECTORY: ${WORKTREE_PATHS[frontend]}

CRITICAL: Change to worktree directory FIRST:
```bash
cd ${WORKTREE_PATHS[frontend]}
```

EPIC SPECIFICATION:

[Read ${EPIC_DIR}/spec.md]

ARCHITECTURE:

[Read ${EPIC_DIR}/architecture.md]

PRESCRIPTIVE PLAN (frontend domain only):

$(echo "$PARALLEL_PLAN" | jq -r '.parallel_plan.frontend.task_description')

FILES TO CREATE/MODIFY (frontend domain):

$(echo "$PARALLEL_PLAN" | jq -r '.parallel_plan.frontend.files[]')

OUTPUT FILE:
${WORKTREE_PATHS[frontend]}/.workflow/outputs/${ARGUMENTS}/frontend_results.json

BEGIN IMPLEMENTATION.
"""
)'
fi)

# DATABASE DOMAIN (if exists)
$(if echo "$DOMAINS" | grep -q "database"; then
echo 'Task(
    subagent_type="general-purpose",
    description="Database implementation for ${ARGUMENTS}",
    prompt=f"""
YOU ARE: Implementation Agent V1

[Read ~/tier1_workflow_global/implementation/agent_definitions/implementation_agent_v1.md]

DOMAIN BRIEFING:

[Read ~/tier1_workflow_global/implementation/agent_briefings/database_implementation.md]

PROJECT ARCHITECTURE:

[Read ~/tier1_workflow_global/implementation/agent_briefings/project_architecture.md]

WORKTREE DIRECTORY: ${WORKTREE_PATHS[database]}

CRITICAL: Change to worktree directory FIRST:
```bash
cd ${WORKTREE_PATHS[database]}
```

EPIC SPECIFICATION:

[Read ${EPIC_DIR}/spec.md]

ARCHITECTURE:

[Read ${EPIC_DIR}/architecture.md]

PRESCRIPTIVE PLAN (database domain only):

$(echo "$PARALLEL_PLAN" | jq -r '.parallel_plan.database.task_description')

FILES TO CREATE/MODIFY (database domain):

$(echo "$PARALLEL_PLAN" | jq -r '.parallel_plan.database.files[]')

OUTPUT FILE:
${WORKTREE_PATHS[database]}/.workflow/outputs/${ARGUMENTS}/database_results.json

BEGIN IMPLEMENTATION.
"""
)'
fi)
```

**Agent Briefing Selection Logic:**

```bash
# Select domain briefing based on domain name
get_domain_briefing() {
  local domain=$1

  case $domain in
    backend)
      echo "backend_implementation.md"
      ;;
    frontend)
      echo "frontend_implementation.md"
      ;;
    database)
      echo "database_implementation.md"
      ;;
    tests)
      echo "testing_implementation.md"
      ;;
    docs)
      echo "documentation_implementation.md"
      ;;
    *)
      # Default to backend if unknown
      echo "backend_implementation.md"
      ;;
  esac
}
```

**Critical Points:**
- All Task() calls in SINGLE orchestrator message
- Each agent receives absolute worktree path
- First instruction: CD into worktree
- Domain-specific file lists from parallel plan
- Results written to worktree, copied to main repo later

---

## Step 4: Wait for Agent Completion

```bash
echo ""
echo "⏳ Waiting for all agents to complete..."
echo "----------------------------------------------------------------------"
echo ""
echo "Agents are working in parallel:"
for domain in $DOMAINS; do
  echo "  - $domain: ${WORKTREE_PATHS[$domain]}"
done
echo ""
echo "Monitor progress by checking results files:"
echo "  ${WORKTREE_PATHS[*]}/.workflow/outputs/${ARGUMENTS}/*_results.json"
echo ""

# Agents work in parallel
# When all Task() calls complete, orchestrator proceeds
```

**Note:** Orchestrator waits for all Task() calls to complete before proceeding. Claude Code handles this automatically.

---

## Step 5: Collect Results from Worktrees

```bash
echo "📊 Collecting results from parallel agents..."
echo "----------------------------------------------------------------------"
echo ""

# Check each domain's results
declare -A DOMAIN_STATUS
declare -A FILES_CREATED_COUNT
declare -A FILES_MODIFIED_COUNT

TOTAL_SUCCESS=0
TOTAL_FAILED=0
TOTAL_PARTIAL=0

for domain in $DOMAINS; do
  WORKTREE_PATH="${WORKTREE_PATHS[$domain]}"
  RESULT_FILE="${WORKTREE_PATH}/.workflow/outputs/${ARGUMENTS}/${domain}_results.json"

  echo "Domain: $domain"

  if [ -f "$RESULT_FILE" ]; then
    # Parse results
    STATUS=$(jq -r '.status // "unknown"' "$RESULT_FILE")
    FILES_CREATED=$(jq -r '.files_created // [] | length' "$RESULT_FILE")
    FILES_MODIFIED=$(jq -r '.files_modified // [] | length' "$RESULT_FILE")

    DOMAIN_STATUS[$domain]="$STATUS"
    FILES_CREATED_COUNT[$domain]=$FILES_CREATED
    FILES_MODIFIED_COUNT[$domain]=$FILES_MODIFIED

    echo "  Status: $STATUS"
    echo "  Files created: $FILES_CREATED"
    echo "  Files modified: $FILES_MODIFIED"

    # Count statuses
    case $STATUS in
      success)
        TOTAL_SUCCESS=$((TOTAL_SUCCESS + 1))
        ;;
      failed)
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        ;;
      partial)
        TOTAL_PARTIAL=$((TOTAL_PARTIAL + 1))
        ;;
    esac

    # Check for issues
    ISSUES_COUNT=$(jq -r '.issues_encountered // [] | length' "$RESULT_FILE")
    if [ "$ISSUES_COUNT" -gt 0 ]; then
      echo "  ⚠️  Issues encountered: $ISSUES_COUNT"
      jq -r '.issues_encountered[] | "    - \(.description)"' "$RESULT_FILE"
    fi

    # Copy results to main repo
    mkdir -p .workflow/outputs/${ARGUMENTS}
    cp "$RESULT_FILE" .workflow/outputs/${ARGUMENTS}/
    echo "  ✅ Results copied to main repo"

  else
    echo "  ❌ Results file not found: $RESULT_FILE"
    DOMAIN_STATUS[$domain]="missing"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
  fi

  echo ""
done

echo "======================================================================"
echo "Parallel Execution Summary:"
echo "  Total domains: ${#DOMAINS[@]}"
echo "  Success: $TOTAL_SUCCESS"
echo "  Partial: $TOTAL_PARTIAL"
echo "  Failed: $TOTAL_FAILED"
echo "======================================================================"
echo ""
```

**Validation:**
- Check for results file in each worktree
- Parse status, file counts, issues
- Copy results to main repo for aggregation
- Track success/failure counts

---

## Step 6: Aggregate Results

```bash
echo "Aggregating results..."
echo "----------------------------------------------------------------------"

# Create aggregate results JSON
cat > .workflow/outputs/${ARGUMENTS}/phase1_parallel_results.json << EOF
{
  "phase": "1B",
  "execution_mode": "parallel",
  "epic_id": "${ARGUMENTS}",
  "timestamp": "$(date -Iseconds)",
  "domains": $(echo "$DOMAINS" | jq -R . | jq -s .),
  "domain_results": {
$(first=true
for domain in $DOMAINS; do
  if [ "$first" = true ]; then
    first=false
  else
    echo ","
  fi
  echo "    \"$domain\": {"
  echo "      \"status\": \"${DOMAIN_STATUS[$domain]}\","
  echo "      \"worktree_path\": \"${WORKTREE_PATHS[$domain]}\","
  echo "      \"worktree_branch\": \"${WORKTREE_BRANCHES[$domain]}\","
  echo "      \"files_created\": ${FILES_CREATED_COUNT[$domain]:-0},"
  echo "      \"files_modified\": ${FILES_MODIFIED_COUNT[$domain]:-0},"
  echo "      \"result_file\": \".workflow/outputs/${ARGUMENTS}/${domain}_results.json\""
  echo -n "    }"
done
echo "")
  },
  "summary": {
    "total_domains": ${#DOMAINS[@]},
    "successful": $TOTAL_SUCCESS,
    "partial": $TOTAL_PARTIAL,
    "failed": $TOTAL_FAILED,
    "overall_status": "$(if [ $TOTAL_FAILED -gt 0 ]; then echo "failed"; elif [ $TOTAL_PARTIAL -gt 0 ]; then echo "partial"; else echo "success"; fi)"
  }
}
EOF

echo "✅ Aggregate results written to:"
echo "   .workflow/outputs/${ARGUMENTS}/phase1_parallel_results.json"
echo ""

# Display summary
OVERALL_STATUS=$(jq -r '.summary.overall_status' .workflow/outputs/${ARGUMENTS}/phase1_parallel_results.json)

echo "======================================================================"
echo "✅ Phase 1B Complete: Parallel Implementation"
echo "======================================================================"
echo "Overall Status: $OVERALL_STATUS"
echo ""
echo "Domain Results:"
for domain in $DOMAINS; do
  status="${DOMAIN_STATUS[$domain]}"
  status_icon="✅"
  [ "$status" = "failed" ] && status_icon="❌"
  [ "$status" = "partial" ] && status_icon="⚠️"
  [ "$status" = "missing" ] && status_icon="❌"

  echo "  $status_icon $domain: $status"
  echo "     Created: ${FILES_CREATED_COUNT[$domain]:-0} files"
  echo "     Modified: ${FILES_MODIFIED_COUNT[$domain]:-0} files"
done
echo ""
echo "Next Phase: Phase 2 (Validation) or Phase 1C (Merge)"
echo "======================================================================"
```

**Aggregate Results Structure:**
```json
{
  "phase": "1B",
  "execution_mode": "parallel",
  "epic_id": "EPIC-007",
  "timestamp": "2025-10-19T14:30:00+00:00",
  "domains": ["backend", "frontend", "database"],
  "domain_results": {
    "backend": {
      "status": "success",
      "worktree_path": ".worktrees/EPIC-007-backend-a3f2b1",
      "worktree_branch": "feature/EPIC-007/backend",
      "files_created": 5,
      "files_modified": 3,
      "result_file": ".workflow/outputs/EPIC-007/backend_results.json"
    },
    "frontend": { ... },
    "database": { ... }
  },
  "summary": {
    "total_domains": 3,
    "successful": 3,
    "partial": 0,
    "failed": 0,
    "overall_status": "success"
  }
}
```

---

## Error Handling

### Worktree Creation Failure

```bash
# If worktree creation fails for any domain, abort
if [ $? -ne 0 ]; then
  echo "❌ Failed to create worktree for $domain"
  echo "   Cleaning up already created worktrees..."

  # Cleanup partial worktrees
  python3 << EOF
import sys
sys.path.insert(0, "$WORKTREE_MANAGER")
from worktree_manager import cleanup_epic_worktrees

try:
    count = cleanup_epic_worktrees("${ARGUMENTS}", delete_branches=True)
    print(f"Cleaned up {count} worktrees")
except Exception as e:
    print(f"Cleanup error: {e}")
EOF

  echo "❌ Phase 1B aborted - falling back to sequential execution"
  exit 1
fi
```

### Agent Failure

```bash
# If any agent fails, mark overall status but continue
if [ "$TOTAL_FAILED" -gt 0 ]; then
  echo "⚠️  $TOTAL_FAILED domain(s) failed"
  echo "   Review individual results for details:"

  for domain in $DOMAINS; do
    if [ "${DOMAIN_STATUS[$domain]}" = "failed" ]; then
      echo "     - $domain: .workflow/outputs/${ARGUMENTS}/${domain}_results.json"
    fi
  done

  echo ""
  echo "⚠️  Phase 1B completed with failures"
  echo "   Manual intervention may be required before merge"
fi
```

### Missing Results File

```bash
# If results file missing, mark as failed
if [ ! -f "$RESULT_FILE" ]; then
  echo "  ❌ Agent did not produce results file"
  echo "     Expected: $RESULT_FILE"

  DOMAIN_STATUS[$domain]="missing"

  # Create placeholder results
  cat > ".workflow/outputs/${ARGUMENTS}/${domain}_results.json" << EOF
{
  "status": "failed",
  "epic_id": "${ARGUMENTS}",
  "domain": "$domain",
  "error": "Agent did not produce results file",
  "completion_timestamp": "$(date -Iseconds)"
}
EOF
fi
```

---

## Important Notes

### 1. Single Message Deployment

**CRITICAL:** All Task() calls MUST be in a single orchestrator message.

✅ **CORRECT:**
```
Orchestrator: "Deploy agents for backend, frontend, database..."
Task(backend)
Task(frontend)
Task(database)
```

❌ **WRONG:**
```
Orchestrator: "Deploy backend agent..."
Task(backend)
[Wait]
Orchestrator: "Deploy frontend agent..."
Task(frontend)
```

### 2. Absolute Paths

Agents receive **absolute paths** to worktrees, not relative:
- ✅ `/home/user/project/.worktrees/EPIC-007-backend-a3f2b1`
- ❌ `.worktrees/EPIC-007-backend-a3f2b1`

### 3. First Instruction: CD

Every agent prompt MUST start with:
```bash
cd /absolute/path/to/worktree
```

This ensures all file operations happen in isolation.

### 4. Domain-Specific Files

Each agent receives ONLY files for their domain:
- Backend agent: `src/backend/`, `backend/`
- Frontend agent: `src/frontend/`, `frontend/`
- Database agent: `src/migrations/`, `database/`

Extracted from parallel plan's domain-specific file lists.

### 5. Results Location

Results written to worktree first, then copied to main repo:
- Worktree: `{worktree}/.workflow/outputs/{epic_id}/{domain}_results.json`
- Main repo: `.workflow/outputs/{epic_id}/{domain}_results.json`

### 6. Metadata Tracking

Worktree manager automatically tracks:
- Worktree creation timestamp
- Branch name
- Status (created → assigned → in_progress → completed)
- Commits made in worktree

Metadata stored in: `.worktrees/.metadata/{worktree_name}.json`

---

## Integration with Phase 1C (Merge)

After Phase 1B completes, Phase 1C handles sequential merge:

1. **Load aggregate results** from Phase 1B
2. **Verify all agents completed** successfully
3. **Sequential merge** in dependency order (database → backend → frontend)
4. **Conflict detection** and handling
5. **Cleanup worktrees** after successful merge

See: `PHASE1C_PARALLEL_MERGE.md` (to be created)

---

## Validation Checklist

Before completing Phase 1B, verify:

- [ ] Parallel plan loaded from Phase 0
- [ ] Worktree created for each domain
- [ ] Worktree paths stored (absolute)
- [ ] All Task() calls in single message
- [ ] Worktree path passed to each agent
- [ ] CD instruction at start of agent prompt
- [ ] Domain-specific briefing selected
- [ ] Domain-specific file list provided
- [ ] Results collected from all worktrees
- [ ] Results copied to main repo
- [ ] Aggregate results JSON created
- [ ] Overall status determined
- [ ] Clear status indicators displayed

---

## Example Output

```
🔀 Phase 1B: Parallel Implementation
======================================================================

Parallel execution across domains:
  - backend: 8 files
    Task: Implement backend API endpoints for user authentication...
  - frontend: 6 files
    Task: Create frontend UI components for user login and profile...
  - database: 3 files
    Task: Add database migrations for user tables and indexes...

Creating isolated worktrees...
----------------------------------------------------------------------
  Creating worktree for: backend
    ✅ Created: .worktrees/EPIC-007-backend-a3f2b1c4
    Branch: feature/EPIC-007/backend
  Creating worktree for: frontend
    ✅ Created: .worktrees/EPIC-007-frontend-d5e6f7g8
    Branch: feature/EPIC-007/frontend
  Creating worktree for: database
    ✅ Created: .worktrees/EPIC-007-database-h9i0j1k2
    Branch: feature/EPIC-007/database

✅ All worktrees created successfully

Deploying parallel agents...
----------------------------------------------------------------------

⚠️  IMPORTANT: Agents will work in parallel. Do not interrupt.

⏳ Waiting for all agents to complete...
----------------------------------------------------------------------

Agents are working in parallel:
  - backend: .worktrees/EPIC-007-backend-a3f2b1c4
  - frontend: .worktrees/EPIC-007-frontend-d5e6f7g8
  - database: .worktrees/EPIC-007-database-h9i0j1k2

[Agents execute in parallel...]

📊 Collecting results from parallel agents...
----------------------------------------------------------------------

Domain: backend
  Status: success
  Files created: 5
  Files modified: 3
  ✅ Results copied to main repo

Domain: frontend
  Status: success
  Files created: 4
  Files modified: 2
  ✅ Results copied to main repo

Domain: database
  Status: success
  Files created: 3
  Files modified: 0
  ✅ Results copied to main repo

======================================================================
Parallel Execution Summary:
  Total domains: 3
  Success: 3
  Partial: 0
  Failed: 0
======================================================================

Aggregating results...
----------------------------------------------------------------------
✅ Aggregate results written to:
   .workflow/outputs/EPIC-007/phase1_parallel_results.json

======================================================================
✅ Phase 1B Complete: Parallel Implementation
======================================================================
Overall Status: success

Domain Results:
  ✅ backend: success
     Created: 5 files
     Modified: 3 files
  ✅ frontend: success
     Created: 4 files
     Modified: 2 files
  ✅ database: success
     Created: 3 files
     Modified: 0 files

Next Phase: Phase 2 (Validation) or Phase 1C (Merge)
======================================================================
```

---

## Performance Metrics

**Expected Performance:**
- Worktree creation: ~5-10 seconds total
- Agent deployment: Instantaneous (parallel)
- Agent execution: Varies by complexity (typically 5-30 minutes)
- Results collection: ~1-2 seconds
- Aggregation: <1 second

**Speedup:**
- Sequential: Sum of all agent times (e.g., 30 + 25 + 15 = 70 minutes)
- Parallel: Max of any agent time (e.g., max(30, 25, 15) = 30 minutes)
- **Speedup: 2-4x** depending on domain complexity and file overlap

---

## Completion

Phase 1B is complete when:

1. ✅ All worktrees created successfully
2. ✅ All agents deployed and executed
3. ✅ All results collected from worktrees
4. ✅ Aggregate results JSON written
5. ✅ Overall status determined
6. ✅ Summary displayed

**Outputs:**
- `.workflow/outputs/{epic_id}/phase1_parallel_results.json` - Aggregate results
- `.workflow/outputs/{epic_id}/{domain}_results.json` - Per-domain results
- `.worktrees/.metadata/{worktree_name}.json` - Worktree metadata

**Next Steps:**
- Phase 1C: Sequential merge of worktrees
- Phase 2: Validation (build, lint, architecture checks)
- Cleanup: Remove worktrees after successful merge
