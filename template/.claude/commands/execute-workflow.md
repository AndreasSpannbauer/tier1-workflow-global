---
description: "Execute Tier 1 workflow for epic implementation (sequential or parallel)"
argument-hint: "<epic-id>"
allowed-tools: [Read, Write, Bash, Task]
---

# Execute Tier 1 Workflow - Sequential and Parallel Execution

YOU are the ORCHESTRATOR. Agents are WORKERS. You coordinate, they execute.

This command executes the complete Tier 1 workflow for a given epic, supporting both sequential and parallel execution modes.

---

## PHASE 0: PREFLIGHT CHECKS

Verify the epic is ready for execution before deploying any agents.

### Step 0.1: Find Epic Directory

```bash
EPIC_DIR=$(find .tasks -name "${ARGUMENTS}-*" -type d | head -1)
```

If not found:
```
❌ Epic directory not found for: ${ARGUMENTS}
Check: .tasks/backlog/${ARGUMENTS}-*/
Run: /task-list to view available epics
```

### Step 0.2: Verify Required Files

Check the following files exist and are complete:

```bash
# Required files
[ -f "${EPIC_DIR}/spec.md" ] || echo "MISSING: spec.md"
[ -f "${EPIC_DIR}/architecture.md" ] || echo "MISSING: architecture.md"
[ -f "${EPIC_DIR}/implementation-details/file-tasks.md" ] || echo "MISSING: file-tasks.md"
```

**Expected files:**
- ✅ `spec.md` - Epic specification with problem statement and requirements
- ✅ `architecture.md` - Architecture decisions and design
- ✅ `implementation-details/file-tasks.md` - Prescriptive implementation plan

If any files are missing:
```
❌ Epic not ready for execution

Missing files:
- [list missing files]

Run: /refine-epic ${ARGUMENTS}
```

### Step 0.3: Verify Git Working Directory

Check that the working directory is clean before starting:

```bash
git status --porcelain
```

If output is not empty:
```
❌ Git working directory not clean

Uncommitted changes detected:
[show git status output]

Commit or stash changes before running workflow:
git add .
git commit -m "Your commit message"

OR

git stash
```

### Step 0.4: Parallel Execution Detection

Analyze file-tasks.md to determine if parallel execution is viable:

```bash
echo ""
echo "🔍 Analyzing for parallel execution opportunities..."

# Run parallel detection
PARALLEL_ANALYSIS=$(python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  "${EPIC_DIR}/implementation-details/file-tasks.md")

# Parse results
PARALLEL_VIABLE=$(echo "$PARALLEL_ANALYSIS" | jq -r '.viable')
PARALLEL_REASON=$(echo "$PARALLEL_ANALYSIS" | jq -r '.reason')
FILE_COUNT=$(echo "$PARALLEL_ANALYSIS" | jq -r '.file_count')
DOMAIN_COUNT=$(echo "$PARALLEL_ANALYSIS" | jq -r '.domain_count')

# Save analysis for later phases
mkdir -p .workflow/outputs/${ARGUMENTS}
echo "$PARALLEL_ANALYSIS" > .workflow/outputs/${ARGUMENTS}/parallel_analysis.json

echo ""
echo "Parallel Analysis:"
echo "  Files: $FILE_COUNT"
echo "  Domains: $DOMAIN_COUNT"
echo "  Viable: $PARALLEL_VIABLE"
echo "  Reason: $PARALLEL_REASON"
echo ""

# Set execution mode
if [ "$PARALLEL_VIABLE" = "true" ]; then
  EXECUTION_MODE="parallel"
  echo "✅ Parallel execution enabled"
else
  EXECUTION_MODE="sequential"
  echo "➡️ Sequential execution (parallel not viable)"
fi
```

### Step 0.5: Check GitHub CLI Availability (Optional)

Check if GitHub integration is possible:

```bash
# Check if gh CLI is available and authenticated
GITHUB_AVAILABLE=0

if ! command -v gh &> /dev/null; then
  echo "ℹ️ GitHub CLI not found - skipping issue creation"
elif ! gh auth status &> /dev/null 2>&1; then
  echo "ℹ️ GitHub CLI not authenticated - skipping issue creation"
else
  echo "✅ GitHub CLI available and authenticated"
  GITHUB_AVAILABLE=1
fi

# Store for later phases
echo "$GITHUB_AVAILABLE" > .workflow/outputs/${ARGUMENTS}/github_available.txt
```

### Step 0.6: Display Epic Summary

Read and display epic information:

```bash
# Extract epic title
EPIC_TITLE=$(grep "^# " ${EPIC_DIR}/spec.md | head -1 | sed 's/^# //')

echo ""
echo "======================================================================"
echo "✅ Preflight checks passed"
echo "======================================================================"
echo ""
echo "Epic: ${ARGUMENTS}"
echo "Title: ${EPIC_TITLE}"
echo "Files to modify: ${FILE_COUNT}"
echo "Mode: ${EXECUTION_MODE}"
echo ""
```

**If all checks pass, proceed to Phase 1.**

---

## PHASE 1: IMPLEMENTATION

Deploy agents to execute the implementation. Execution path depends on the mode determined in Phase 0.

### Execution Mode Branch

```bash
if [ "$EXECUTION_MODE" = "parallel" ]; then
  # Execute Phase 1B (Parallel Implementation) + Phase 1C (Sequential Merge)
else
  # Execute Phase 1A (Sequential Implementation)
fi
```

---

## PHASE 1A: SEQUENTIAL IMPLEMENTATION

**Condition:** `EXECUTION_MODE == "sequential"`

Deploy a single implementation agent to execute the prescriptive plan.

### Step 1A.1: Read Epic Context

Read the following files to provide full context to the implementation agent:

1. **Specification**: `${EPIC_DIR}/spec.md`
2. **Architecture**: `${EPIC_DIR}/architecture.md`
3. **Prescriptive Plan**: `${EPIC_DIR}/implementation-details/file-tasks.md`

### Step 1A.2: Deploy Implementation Agent

```bash
echo ""
echo "🚀 Phase 1A: Sequential Implementation"
echo "======================================================================"
echo ""
```

Use the Task tool to deploy an implementation agent with the complete context.

**Agent Definition Location**: `~/tier1_workflow_global/implementation/agent_definitions/implementation_agent_v1.md`

**Domain Briefing Location** (select appropriate domain based on file-tasks.md):
- Backend: `~/tier1_workflow_global/implementation/agent_briefings/backend_implementation.md`
- Frontend: `~/tier1_workflow_global/implementation/agent_briefings/frontend_implementation.md`
- Database: `~/tier1_workflow_global/implementation/agent_briefings/database_implementation.md`

**Project Architecture**: `~/tier1_workflow_global/implementation/agent_briefings/project_architecture.md`

**Agent Prompt Template:**

```markdown
YOU ARE: Implementation Agent V1

[Read ~/tier1_workflow_global/implementation/agent_definitions/implementation_agent_v1.md]

---

DOMAIN BRIEFING:

[Read ~/tier1_workflow_global/implementation/agent_briefings/backend_implementation.md]
(or appropriate domain briefing)

---

PROJECT ARCHITECTURE:

[Read ~/tier1_workflow_global/implementation/agent_briefings/project_architecture.md]

---

EPIC SPECIFICATION:

[Read ${EPIC_DIR}/spec.md]

---

ARCHITECTURE:

[Read ${EPIC_DIR}/architecture.md]

---

PRESCRIPTIVE PLAN (YOUR SOURCE OF TRUTH):

[Read ${EPIC_DIR}/implementation-details/file-tasks.md]

---

OUTPUT FILE:

Write your structured results to:
.workflow/outputs/${ARGUMENTS}/phase1_results.json

Format:
{
  "status": "success|partial|failed",
  "epic_id": "${ARGUMENTS}",
  "agent_type": "implementation-agent-v1",
  "execution_mode": "sequential",
  "files_created": ["path/to/file1.py", "path/to/file2.py"],
  "files_modified": ["path/to/existing_file.py"],
  "issues_encountered": [
    {
      "description": "Issue description",
      "file": "path/to/file.py",
      "resolution": "How it was resolved"
    }
  ],
  "clarifications_needed": [
    "Any questions or unclear requirements"
  ],
  "completion_timestamp": "2025-10-19T14:30:00Z"
}

---

BEGIN IMPLEMENTATION.

Follow the prescriptive plan exactly. Create and modify files as specified. Add error handling. Write clean, maintainable code. Document any issues in the results JSON.

WHEN COMPLETE: Write results to .workflow/outputs/${ARGUMENTS}/phase1_results.json
```

**Deploy the agent using Task tool:**

```python
Task(
    subagent_type="general-purpose",
    description=f"Sequential implementation for {ARGUMENTS}",
    prompt="""
    [Complete agent prompt from template above]
    """
)
```

### Step 1A.3: Read and Display Results

After agent completes, read the results file:

```bash
echo ""
echo "📊 Reading implementation results..."
echo ""

cat .workflow/outputs/${ARGUMENTS}/phase1_results.json

# Parse status
IMPL_STATUS=$(jq -r '.status' .workflow/outputs/${ARGUMENTS}/phase1_results.json)
FILES_CREATED=$(jq -r '.files_created | length' .workflow/outputs/${ARGUMENTS}/phase1_results.json)
FILES_MODIFIED=$(jq -r '.files_modified | length' .workflow/outputs/${ARGUMENTS}/phase1_results.json)

echo ""
echo "======================================================================"
echo "✅ Phase 1A Complete: Sequential Implementation"
echo "======================================================================"
echo "Status: $IMPL_STATUS"
echo "Files created: $FILES_CREATED"
echo "Files modified: $FILES_MODIFIED"
echo ""
```

**Proceed to Phase 2 (Validation) if status = "success"**

---

## PHASE 1B: PARALLEL IMPLEMENTATION

**Condition:** `EXECUTION_MODE == "parallel"`

Deploy multiple agents in isolated git worktrees for parallel execution.

### Step 1B.1: Load Parallel Plan

```bash
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
```

### Step 1B.2: Create GitHub Epic Issue (Optional)

```bash
if [ "$EXECUTION_MODE" = "parallel" ] && [ "$GITHUB_AVAILABLE" -eq 1 ]; then
  echo ""
  echo "📝 Creating GitHub epic issue..."

  # Extract epic metadata
  EPIC_TITLE=$(grep "^# " ${EPIC_DIR}/spec.md | head -1 | sed 's/^# //')

  # Count domains and files
  TOTAL_FILES=$(echo "$PARALLEL_PLAN" | jq '[.domains[] | length] | add')

  # Generate domain summary
  DOMAIN_SUMMARY=$(for domain in $DOMAINS; do
    file_count=$(echo "$PARALLEL_PLAN" | jq -r ".domains.\"$domain\" | length")
    echo "- **${domain}**: ${file_count} files"
  done)

  # Create issue body
  EPIC_BODY=$(cat << EOF
## Epic: ${ARGUMENTS}

**Execution Mode:** Parallel (${DOMAIN_COUNT} domains, ${TOTAL_FILES} files)

### Specification

$(cat ${EPIC_DIR}/spec.md)

### Architecture

$(cat ${EPIC_DIR}/architecture.md)

### Domains

${DOMAIN_SUMMARY}

### Execution Plan

This epic will be implemented using parallel execution with git worktrees. Each domain will be implemented by an isolated agent in its own worktree, then merged sequentially to prevent conflicts.

### Status

- [x] Phase 0: Preflight ✅
- [ ] Phase 1B: Parallel Implementation (in progress)
- [ ] Phase 1C: Sequential Merge
- [ ] Phase 2: Validation
- [ ] Phase 5: Commit & Cleanup

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)

  # Create epic issue using gh CLI
  EPIC_ISSUE_NUMBER=$(gh issue create \
    --title "${EPIC_TITLE}" \
    --body "${EPIC_BODY}" \
    --label "type:epic,status:in-progress,execution:parallel" \
    --json number \
    --jq '.number' 2>&1)

  if [ $? -eq 0 ]; then
    echo "  ✅ Epic issue created: #${EPIC_ISSUE_NUMBER}"
    echo "${EPIC_ISSUE_NUMBER}" > .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt
  else
    echo "  ⚠️ Epic issue creation failed (non-blocking)"
    echo "" > .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt
  fi
else
  echo "ℹ️ Skipping GitHub epic issue creation"
fi
```

### Step 1B.3: Create Worktrees

```bash
echo ""
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

### Step 1B.4: Create GitHub Sub-Issues (Optional)

```bash
EPIC_ISSUE_NUMBER=$(cat .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt 2>/dev/null)

if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  echo ""
  echo "📝 Creating sub-issues for parallel domains..."

  # Associative array to store sub-issue numbers
  declare -A SUB_ISSUE_NUMBERS

  for domain in $DOMAINS; do
    # Extract domain-specific information
    TASK_DESCRIPTION=$(echo "$PARALLEL_PLAN" | jq -r ".parallel_plan.\"$domain\".task_description")
    DOMAIN_FILES=$(echo "$PARALLEL_PLAN" | jq -r ".parallel_plan.\"$domain\".files[]")
    FILE_COUNT=$(echo "$PARALLEL_PLAN" | jq -r ".parallel_plan.\"$domain\".files | length")

    # Generate file list
    FILE_LIST=$(echo "$DOMAIN_FILES" | while read file; do echo "- \`${file}\`"; done)

    # Create sub-issue body
    SUB_ISSUE_BODY=$(cat << EOF
## ${ARGUMENTS}: ${domain} Implementation

**Parent Epic:** #${EPIC_ISSUE_NUMBER}
**Domain:** ${domain}
**Files:** ${FILE_COUNT}

### Task Description

${TASK_DESCRIPTION}

### Files to Create/Modify

${FILE_LIST}

### Execution Details

This task will be executed by an isolated agent in a dedicated git worktree:
- **Branch:** \`feature/${ARGUMENTS}/${domain}\`
- **Worktree:** \`.worktrees/${ARGUMENTS}-${domain}-<hash>/\`

After implementation, this branch will be merged sequentially into the target branch.

### Status

- [ ] Implementation (in progress)
- [ ] Validation
- [ ] Merge

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)

    # Create sub-issue
    SUB_ISSUE_NUMBER=$(gh issue create \
      --title "${ARGUMENTS}: ${domain} Implementation" \
      --body "${SUB_ISSUE_BODY}" \
      --label "type:task,domain:${domain},status:in-progress,parent:${EPIC_ISSUE_NUMBER}" \
      --json number \
      --jq '.number' 2>&1)

    if [ $? -eq 0 ]; then
      SUB_ISSUE_NUMBERS[$domain]="$SUB_ISSUE_NUMBER"
      echo "  ✅ Sub-issue created for ${domain}: #${SUB_ISSUE_NUMBER}"

      # Link to parent epic
      gh issue comment ${EPIC_ISSUE_NUMBER} \
        --body "🔗 Sub-task created: #${SUB_ISSUE_NUMBER} (${domain})" \
        2>&1 > /dev/null || echo "  ⚠️ Failed to link sub-issue to epic (non-blocking)"
    else
      echo "  ⚠️ Sub-issue creation failed for ${domain} (non-blocking)"
      SUB_ISSUE_NUMBERS[$domain]=""
    fi
  done

  # Store sub-issue numbers as JSON
  SUB_ISSUES_JSON=$(cat << EOF
{
  "epic_issue": ${EPIC_ISSUE_NUMBER},
  "sub_issues": {
$(for domain in $DOMAINS; do
  sub_num="${SUB_ISSUE_NUMBERS[$domain]}"
  [ -n "$sub_num" ] && echo "    \"$domain\": ${sub_num}," || echo "    \"$domain\": null,"
done | sed '$ s/,$//')
  }
}
EOF
)

  echo "$SUB_ISSUES_JSON" > .workflow/outputs/${ARGUMENTS}/github_sub_issues.json

  echo ""
  echo "✅ GitHub issues created:"
  echo "   Epic: #${EPIC_ISSUE_NUMBER}"
  for domain in $DOMAINS; do
    sub_num="${SUB_ISSUE_NUMBERS[$domain]}"
    [ -n "$sub_num" ] && echo "   ${domain}: #${sub_num}"
  done
  echo ""

else
  echo "ℹ️ Skipping GitHub sub-issue creation (no epic issue)"
fi
```

### Step 1B.5: Deploy Parallel Agents

**CRITICAL:** All Task() calls must be in a SINGLE message for parallel execution.

```bash
echo "Deploying parallel agents..."
echo "----------------------------------------------------------------------"
echo ""
echo "⚠️  IMPORTANT: Agents will work in parallel. Do not interrupt."
echo ""
```

**Domain Briefing Selection Helper:**

```bash
# Function to select domain briefing
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

**Deploy agents for each domain (ALL IN THIS SINGLE MESSAGE):**

For each domain in `$DOMAINS`, deploy an agent with this template:

```python
# Example for BACKEND domain
Task(
    subagent_type="general-purpose",
    description=f"Backend implementation for {ARGUMENTS}",
    prompt=f"""
YOU ARE: Implementation Agent V1

[Read ~/tier1_workflow_global/implementation/agent_definitions/implementation_agent_v1.md]

DOMAIN BRIEFING:

[Read ~/tier1_workflow_global/implementation/agent_briefings/backend_implementation.md]

PROJECT ARCHITECTURE:

[Read ~/tier1_workflow_global/implementation/agent_briefings/project_architecture.md]

WORKTREE DIRECTORY: {WORKTREE_PATHS[backend]}

CRITICAL: Change to worktree directory FIRST:
```bash
cd {WORKTREE_PATHS[backend]}
```

ALL file operations must happen in this directory. You are working in ISOLATION.

EPIC SPECIFICATION:

[Read {EPIC_DIR}/spec.md]

ARCHITECTURE:

[Read {EPIC_DIR}/architecture.md]

PRESCRIPTIVE PLAN (backend domain only):

{echo "$PARALLEL_PLAN" | jq -r '.parallel_plan.backend.task_description'}

FILES TO CREATE/MODIFY (backend domain):

{echo "$PARALLEL_PLAN" | jq -r '.parallel_plan.backend.files[]'}

EXECUTION INSTRUCTIONS:

1. CD into worktree: `cd {WORKTREE_PATHS[backend]}`
2. Verify you're in correct directory: `pwd`
3. Follow prescriptive plan for backend files only
4. Create/modify files as specified
5. Add error handling
6. Validate syntax (Python: `python -m py_compile`, TypeScript: `tsc --noEmit`)
7. Write results JSON

OUTPUT FILE:
{WORKTREE_PATHS[backend]}/.workflow/outputs/{ARGUMENTS}/backend_results.json

Format:
{{
  "status": "success|partial|failed",
  "epic_id": "{ARGUMENTS}",
  "domain": "backend",
  "worktree_path": "{WORKTREE_PATHS[backend]}",
  "files_created": [...],
  "files_modified": [...],
  "issues_encountered": [...],
  "completion_timestamp": "2025-10-19T14:30:00Z"
}}

BEGIN IMPLEMENTATION.
"""
)

# Repeat for FRONTEND, DATABASE, and other domains as detected in $DOMAINS
```

**Note:** The orchestrator must construct Task() calls for ALL domains in a single message.

### Step 1B.6: Wait for Agent Completion

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
```

### Step 1B.7: Collect Results from Worktrees

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

### Step 1B.8: Aggregate Results

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
```

### Step 1B.9: Update GitHub Epic Progress (Optional)

```bash
EPIC_ISSUE_NUMBER=$(cat .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt 2>/dev/null)

if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  echo ""
  echo "📝 Updating epic issue with Phase 1B progress..."

  # Read sub-issues
  SUB_ISSUES_JSON=$(cat .workflow/outputs/${ARGUMENTS}/github_sub_issues.json 2>/dev/null)

  # Create progress comment
  PROGRESS_COMMENT=$(cat << EOF
## Phase 1B Complete: Parallel Implementation ✅

All domain implementations have completed. Results:

$(for domain in $DOMAINS; do
  SUB_ISSUE=$(echo "$SUB_ISSUES_JSON" | jq -r ".sub_issues.\"$domain\"" 2>/dev/null)
  STATUS="${DOMAIN_STATUS[$domain]}"

  if [ "$STATUS" = "success" ]; then
    echo "- ✅ **${domain}**: Success (#${SUB_ISSUE})"
  elif [ "$STATUS" = "partial" ]; then
    echo "- ⚠️ **${domain}**: Partial (#${SUB_ISSUE})"
  else
    echo "- ❌ **${domain}**: Failed/Unknown (#${SUB_ISSUE})"
  fi
done)

**Next Phase:** Sequential merge (Phase 1C)

---
Updated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF
)

  # Post comment
  gh issue comment ${EPIC_ISSUE_NUMBER} --body "${PROGRESS_COMMENT}" 2>&1 > /dev/null

  if [ $? -eq 0 ]; then
    echo "  ✅ Progress updated on epic issue #${EPIC_ISSUE_NUMBER}"
  else
    echo "  ⚠️ Failed to update epic issue (non-blocking)"
  fi

else
  echo "ℹ️ Skipping epic progress update (no epic issue)"
fi
```

**Proceed to Phase 1C (Sequential Merge)**

---

## PHASE 1C: SEQUENTIAL MERGE

**Condition:** `EXECUTION_MODE == "parallel"` (runs after Phase 1B)

Sequentially merge worktree branches back into the main branch in dependency order.

### Step 1C.1: Verify All Agents Succeeded

```bash
echo ""
echo "🔗 Phase 1C: Sequential Merge"
echo "======================================================================"
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

### Step 1C.2: Determine Merge Order

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

### Step 1C.3: Sequential Merge with Conflict Detection

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

### Step 1C.4: Handle Merge Conflicts

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

### Step 1C.5: Verify Merge Success

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

### Step 1C.6: Close GitHub Sub-Issues (Optional)

```bash
EPIC_ISSUE_NUMBER=$(cat .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt 2>/dev/null)
SUB_ISSUES_JSON=$(cat .workflow/outputs/${ARGUMENTS}/github_sub_issues.json 2>/dev/null)

if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  echo ""
  echo "📝 Closing sub-issues after merge..."

  for domain in "${ORDERED_DOMAINS[@]}"; do
    SUB_ISSUE=$(echo "$SUB_ISSUES_JSON" | jq -r ".sub_issues.\"$domain\"" 2>/dev/null)

    if [ -n "$SUB_ISSUE" ] && [ "$SUB_ISSUE" != "null" ]; then
      # Close sub-issue with merge confirmation
      gh issue close ${SUB_ISSUE} \
        --comment "✅ Merged successfully into main branch

**Merge Details:**
- Branch: \`feature/${ARGUMENTS}/${domain}\`
- Merged at: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
- Merge strategy: Sequential (no-fast-forward)

This sub-task is complete." 2>&1 > /dev/null

      if [ $? -eq 0 ]; then
        echo "  ✅ Closed sub-issue #${SUB_ISSUE} (${domain})"
      else
        echo "  ⚠️ Failed to close sub-issue #${SUB_ISSUE} (non-blocking)"
      fi
    fi
  done

  # Update epic with merge completion
  MERGE_COMMENT=$(cat << EOF
## Phase 1C Complete: Sequential Merge ✅

All domain branches have been merged successfully into the target branch.

**Merge Order:**
$(for domain in "${ORDERED_DOMAINS[@]}"; do
  echo "1. ${domain} → merged"
done)

**Conflicts:** None detected
**Sub-issues:** All closed

**Next Phase:** Validation (Phase 2)

---
Updated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF
)

  gh issue comment ${EPIC_ISSUE_NUMBER} --body "${MERGE_COMMENT}" 2>&1 > /dev/null

  if [ $? -eq 0 ]; then
    echo "  ✅ Merge completion posted to epic issue"
  fi

else
  echo "ℹ️ Skipping sub-issue closure (no epic issue)"
fi
```

### Step 1C.7: Cleanup Worktrees

```bash
echo ""
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
echo ""
```

### Step 1C.8: Create Merge Summary

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

echo "======================================================================"
echo "✅ Phase 1C Complete: Sequential Merge"
echo "======================================================================"
echo "   Merge summary: .workflow/outputs/${ARGUMENTS}/merge_summary.json"
echo ""
```

**Proceed to Phase 2 (Validation)**

---

## PHASE 2: VALIDATION

Validate the implementation with automated checks.

**Note:** This phase runs the same regardless of execution mode (sequential or parallel).

### Step 2.1: Run Validation Checks

```bash
echo ""
echo "🔍 Phase 2: Validation"
echo "======================================================================"
echo ""

# Build & Lint Gate (mandatory)
echo "Running build and lint checks..."

# Python validation
if [ -d "src" ] && grep -q "\.py$" .workflow/outputs/${ARGUMENTS}/phase1_results.json 2>/dev/null; then
  echo "  Python validation:"
  ruff check . && echo "    ✅ Ruff check passed" || echo "    ❌ Ruff check failed"
  mypy src/ && echo "    ✅ Mypy check passed" || echo "    ❌ Mypy check failed"
fi

# TypeScript validation
if [ -f "tsconfig.json" ]; then
  echo "  TypeScript validation:"
  npm run build:ts && echo "    ✅ TypeScript build passed" || echo "    ❌ TypeScript build failed"
fi

echo ""
echo "✅ Phase 2 Complete: Validation"
echo ""
```

### Step 2.2: Update GitHub Epic Labels (Optional)

```bash
EPIC_ISSUE_NUMBER=$(cat .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt 2>/dev/null)

if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  echo "📝 Updating epic labels: status:in-progress → status:validation"

  gh issue edit ${EPIC_ISSUE_NUMBER} \
    --remove-label "status:in-progress" \
    --add-label "status:validation" 2>&1 > /dev/null

  if [ $? -eq 0 ]; then
    echo "  ✅ Epic labels updated for Phase 2"
  else
    echo "  ⚠️ Failed to update epic labels (non-blocking)"
  fi
fi
```

**Proceed to Phase 5 (Commit & Cleanup)**

---

## PHASE 5: COMMIT & CLEANUP

Create commit, move epic to completed, and close GitHub issues.

### Step 5.1: Generate Commit Message

```bash
echo ""
echo "📝 Phase 5: Commit & Cleanup"
echo "======================================================================"
echo ""

# Extract epic title
EPIC_TITLE=$(grep "^# " ${EPIC_DIR}/spec.md | head -1 | sed 's/^# //')

# Count changes
if [ "$EXECUTION_MODE" = "parallel" ]; then
  TOTAL_FILES_CREATED=$(jq '[.domain_results[].files_created] | add' .workflow/outputs/${ARGUMENTS}/phase1_parallel_results.json)
  TOTAL_FILES_MODIFIED=$(jq '[.domain_results[].files_modified] | add' .workflow/outputs/${ARGUMENTS}/phase1_parallel_results.json)
else
  TOTAL_FILES_CREATED=$(jq '.files_created | length' .workflow/outputs/${ARGUMENTS}/phase1_results.json)
  TOTAL_FILES_MODIFIED=$(jq '.files_modified | length' .workflow/outputs/${ARGUMENTS}/phase1_results.json)
fi

# Generate commit message
COMMIT_MESSAGE=$(cat << EOF
feat(${ARGUMENTS}): ${EPIC_TITLE}

Implementation completed using ${EXECUTION_MODE} execution mode.

Files created: ${TOTAL_FILES_CREATED}
Files modified: ${TOTAL_FILES_MODIFIED}
Execution mode: ${EXECUTION_MODE}
$(if [ "$EXECUTION_MODE" = "parallel" ]; then
  echo "Domains: $(echo "${ORDERED_DOMAINS[@]}" | tr ' ' ', ')"
fi)

Epic: ${EPIC_DIR}
Results: .workflow/outputs/${ARGUMENTS}/

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)

echo "Commit message:"
echo "----------------------------------------------------------------------"
echo "$COMMIT_MESSAGE"
echo "----------------------------------------------------------------------"
echo ""
```

### Step 5.2: Create Commit

```bash
# Stage changes
git add .

# Create commit
git commit -m "$(cat <<'EOF'
$COMMIT_MESSAGE
EOF
)"

if [ $? -eq 0 ]; then
  echo "✅ Commit created successfully"
else
  echo "❌ Commit failed"
  exit 1
fi

echo ""
```

### Step 5.3: Move Epic to Completed

```bash
echo "Moving epic to completed..."

COMPLETED_DIR=".tasks/completed"
mkdir -p "$COMPLETED_DIR"

mv "$EPIC_DIR" "$COMPLETED_DIR/"

if [ $? -eq 0 ]; then
  echo "✅ Epic moved to: $COMPLETED_DIR/$(basename $EPIC_DIR)"
else
  echo "⚠️ Failed to move epic to completed (non-critical)"
fi

echo ""
```

### Step 5.4: Close GitHub Epic Issue (Optional)

```bash
EPIC_ISSUE_NUMBER=$(cat .workflow/outputs/${ARGUMENTS}/github_epic_issue.txt 2>/dev/null)

if [ -n "$EPIC_ISSUE_NUMBER" ]; then
  echo "📝 Closing epic issue..."

  gh issue close ${EPIC_ISSUE_NUMBER} \
    --comment "✅ Workflow complete - all phases passed

**Final Status:**
- Implementation: ✅ ${EXECUTION_MODE} execution successful
- Validation: ✅ Build/lint/architecture checks passed
- Commit: ✅ Changes committed to repository

**Artifacts:**
- Post-mortem: \`.workflow/post-mortem/${ARGUMENTS}.md\`
- Implementation results: \`.workflow/outputs/${ARGUMENTS}/\`

This epic is complete and can be closed.

---
Completed: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" 2>&1 > /dev/null

  if [ $? -eq 0 ]; then
    echo "  ✅ Epic issue closed successfully"
  else
    echo "  ⚠️ Failed to close epic issue (non-blocking)"
  fi
else
  echo "ℹ️ Skipping epic issue closure (no epic issue)"
fi
```

---

## COMPLETION SUMMARY

```bash
echo ""
echo "======================================================================"
echo "✅ Workflow Complete: ${ARGUMENTS}"
echo "======================================================================"
echo ""
echo "Execution mode: ${EXECUTION_MODE}"
echo "Epic: ${EPIC_TITLE}"
echo "Files created: ${TOTAL_FILES_CREATED}"
echo "Files modified: ${TOTAL_FILES_MODIFIED}"
echo ""
echo "Results:"
echo "  - Implementation: .workflow/outputs/${ARGUMENTS}/"
echo "  - Epic moved to: .tasks/completed/$(basename $EPIC_DIR)"
echo ""
echo "Git:"
echo "  - Commit created: $(git rev-parse --short HEAD)"
echo "  - Branch: $(git branch --show-current)"
echo ""
echo "Next steps:"
echo "  1. Review commit: git show"
echo "  2. Push changes: git push"
echo "  3. Create pull request (if applicable)"
echo ""
echo "======================================================================"
```

---

## ERROR HANDLING

### Epic Not Found
```
❌ Error: Epic directory not found

Epic ID: ${ARGUMENTS}
Searched: .tasks/backlog/
         .tasks/current/

Available epics:
[list epics in .tasks/]

Run: /task-list
```

### Missing Files
```
❌ Error: Required files missing

Epic: ${ARGUMENTS}
Missing:
- spec.md [create with /spec-epic ${ARGUMENTS}]
- architecture.md [create with /spec-epic ${ARGUMENTS}]
- file-tasks.md [create with /refine-epic ${ARGUMENTS}]

Fix: Complete epic specification before running workflow
```

### Git Not Clean
```
❌ Error: Git working directory not clean

Uncommitted changes:
[git status output]

Options:
1. Commit changes: git add . && git commit -m "message"
2. Stash changes: git stash
3. Reset changes: git reset --hard (WARNING: destructive)

Run workflow after working directory is clean.
```

### Worktree Creation Failed
```
❌ Error: Worktree creation failed

Domain: ${domain}
Error: [error message]

Cleanup partial worktrees:
python3 ~/tier1_workflow_global/implementation/worktree_manager/cleanup.py ${ARGUMENTS}

Retry workflow after cleanup.
```

### Merge Conflicts
```
⚠️ Merge conflicts detected in: [domains]

Manual resolution required.
See: .workflow/outputs/${ARGUMENTS}/merge_conflicts.json

Steps to resolve:
1. Manually merge conflicted branches
2. Resolve conflicts in editor
3. Stage changes: git add .
4. Commit: git commit
5. Resume workflow: /execute-workflow ${ARGUMENTS} --resume
```

---

## PROGRESS INDICATORS

Use these throughout execution:

- ✅ Success / Completed
- ⚠️ Warning / Partial completion
- ❌ Error / Failed
- 🔍 Checking / Validating
- 📝 Reading / Parsing
- 🚀 Starting / Executing
- 📊 Results / Summary
- 🔀 Parallel execution
- 🔗 Merging
- 🧹 Cleanup

---

## NOTES FOR ORCHESTRATOR

**Remember:**
1. **You coordinate, agents execute** - Don't do implementation yourself
2. **Read before deploying** - Agents need all context (definition, briefings, spec, plan)
3. **Parallel agents in single message** - All Task() calls for Phase 1B must be in ONE message
4. **Wait for completion** - Don't proceed until agents write results JSON
5. **Parse results** - Understand what happened before declaring success
6. **Handle errors gracefully** - Provide clear guidance for manual intervention
7. **GitHub is optional** - All operations are non-blocking

**Agent Composition:**
- **Agent Definition** = Phase-specific rules (what agent MUST/MUST NOT do)
- **Domain Briefing** = Domain-specific patterns (project conventions, coding standards)
- **Project Architecture** = Project-wide architectural decisions
- **Spec + Architecture** = What to build
- **Prescriptive Plan** = Exactly how to build it (source of truth)

**Execution Modes:**
- **Sequential** (Phase 1A): Single agent, main branch, traditional flow
- **Parallel** (Phase 1B + 1C): Multiple agents, worktrees, sequential merge

**Output Structure:**
- `.workflow/outputs/${ARGUMENTS}/` - All workflow outputs
- `.workflow/outputs/${ARGUMENTS}/parallel_analysis.json` - Parallel detection results
- `.workflow/outputs/${ARGUMENTS}/phase1_results.json` - Sequential implementation results
- `.workflow/outputs/${ARGUMENTS}/phase1_parallel_results.json` - Parallel aggregate results
- `.workflow/outputs/${ARGUMENTS}/merge_summary.json` - Merge results
- `.workflow/outputs/${ARGUMENTS}/github_epic_issue.txt` - GitHub epic issue number
- `.workflow/outputs/${ARGUMENTS}/github_sub_issues.json` - GitHub sub-issue numbers
