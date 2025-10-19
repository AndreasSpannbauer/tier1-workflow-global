# Tier 1 Enhancement Assessment: Porting V6 Workflow to General-Purpose Projects

**Date:** 2025-10-19
**Source Analysis:** email_management_system V6 workflow architecture
**Target:** Tier 1 simplified workflow for all projects (per V6_TIER1_FINAL_IMPLEMENTATION_PLAN.md)
**Assessment Type:** Architecture analysis and implementation strategy

---

## Executive Summary

This assessment analyzes the V6 workflow architecture from email_management_system to identify components suitable for porting to Tier 1 (simplified task management for all projects). The V6 system is a sophisticated, production-grade workflow with:

- **Complete workflow orchestration** (Phases 0-7)
- **Parallel execution with git worktrees**
- **Agent definitions and domain briefings** (phase-specific rules + project-specific context)
- **Multi-layered validation** (architecture, contracts, build, tests)
- **Post-mortem analysis with 3 parallel agents**
- **Knowledge capture and semantic indexing**
- **GitHub integration** (bidirectional sync)

**Key Finding:** The V6 workflow's power comes from:
1. **Orchestrator pattern** - Claude Code session coordinates, phase handlers provide recommendations
2. **Agent/briefing system** - Phase-specific agent rules + domain-specific briefings = consistent quality
3. **Worktree isolation** - Enables true parallel work without conflicts
4. **Explicit validation** - Observable npm scripts, not hidden hooks
5. **Post-mortem learning** - Captures what worked/didn't for continuous improvement

**Recommendation:** Port a **simplified workflow command** to Tier 1 that:
- Keeps orchestration pattern (Claude = orchestrator, agents = workers)
- **Includes agent/briefing system** (CRITICAL: phase rules + domain context)
- Adds parallel execution via worktrees (when beneficial)
- Uses Python-compatible validation (Ruff, mypy, pytest)
- Includes lightweight post-mortem (single agent, not three)
- Skips documentation automation (manual updates preferred)

---

## I. Current V6 Workflow Architecture (email_management_system)

### 1.1 Workflow Command Structure

**File:** `.claude/commands/workflow_v6/w-workflow-v6-mcp.md`

**Key Pattern: Two-Layer Architecture**

```
┌─────────────────────────────────────────┐
│ Claude Code Session (ORCHESTRATOR)      │
│ - Deploys sub-agents via Task tool      │
│ - Makes execution decisions              │
│ - Coordinates parallel work              │
│ - Collects and synthesizes results       │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Phase Handlers (PASSIVE)                │
│ - Generate plans and recommendations    │
│ - Return JSON with instructions          │
│ - NO direct agent execution              │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Sub-Agents (WORKERS)                    │
│ - Execute prescriptive plans             │
│ - Write structured results to files      │
│ - Report completion to orchestrator      │
└─────────────────────────────────────────┘
```

**Orchestration Flow:**

1. **Initialize workflow** - `v6_initialize_workflow(task_id)`
2. **Check status** - `v6_get_workflow_status()` for ready phases
3. **Get recommendations** - `v6_get_phase_results()` for phase outputs
4. **Deploy agents** - Use Task tool with specific briefings
5. **Store results** - `v6_execute_phase(results=...)` to mark complete

**Phase Structure:**

- **Phase 0:** Preflight (system health, git clean, spec complete)
- **Phases 1-4:** Context gathering (analysis, strategy, research, planning)
- **Phase 5A-5F:** Implementation + validation sub-phases
- **Phase 6:** Commit validation
- **Phase 7:** Post-mortem and knowledge capture

**Critical Insight:** The orchestrator NEVER lets phase handlers execute agents directly. This separation keeps workflow observable and debuggable.

### 1.2 Parallel Execution with Git Worktrees

**Files:**
- `tools/worktree_manager/worktree_manager.py`
- `tools/workflow_utilities_v6/interactive_workflow/parallel_execution_manager.py`

**Worktree System Overview:**

```python
# Create isolated worktree for parallel agent
metadata = create_worktree_for_agent(
    epic_id="EPIC-007",
    task_name="Backend API Implementation",
    base_branch="dev"
)
# Result: .worktrees/EPIC-007-backend-api-a3f2b1/
#         (branch: feature/EPIC-007/backend-api)
```

**Key Features:**

1. **Directory Isolation** - Each agent gets its own worktree directory
2. **Branch Isolation** - Separate feature branches per worktree
3. **Metadata Tracking** - `.worktrees/.metadata/*.json` stores worktree state
4. **Safe Cleanup** - Automated worktree removal after merge

**Parallel Detection Logic:**

```python
# Analyze epic for parallel opportunities
parallel_plan = parallel_manager.analyze_for_parallel_execution(
    implementation_plan,  # From Phase 4
    task_id
)

if parallel_plan.enabled:
    # Criteria met: 5+ files, 2+ domains, minimal file overlap
    execution_result = parallel_manager.execute_parallel_workflow(
        parallel_plan,
        spec_data,
        agent_executor
    )
```

**Parallelization Criteria:**
- **Minimum scope:** 5+ files changed across 2+ domains
- **File overlap threshold:** <30% shared files between tasks
- **Domain separation:** Backend, frontend, database, tests, docs
- **Dependency awareness:** Wave-based execution respects task dependencies

**Detailed Implementation Workflow:**

**Phase 1A: Create Worktrees (Orchestrator)**

```bash
# Orchestrator creates worktrees BEFORE deploying agents
python3 tools/worktree_manager/worktree_manager.py create \
  --epic EPIC-007 \
  --task-name "backend" \
  --base-branch dev

python3 tools/worktree_manager/worktree_manager.py create \
  --epic EPIC-007 \
  --task-name "frontend" \
  --base-branch dev

# Result:
# .worktrees/EPIC-007-backend-a3f2b1/  (branch: feature/EPIC-007/backend)
# .worktrees/EPIC-007-frontend-b4e1/  (branch: feature/EPIC-007/frontend)
```

**Phase 1B: Deploy Agents with Worktree Paths**

```python
# Get absolute paths to worktrees
backend_worktree = "/absolute/path/to/.worktrees/EPIC-007-backend-a3f2b1"
frontend_worktree = "/absolute/path/to/.worktrees/EPIC-007-frontend-b4e1"

# Deploy agents in parallel (single message, multiple Task calls)
Task(
  subagent_type="implementation-agent-v1",
  description="Backend implementation",
  prompt=f"""
  WORKTREE DIRECTORY: {backend_worktree}

  CRITICAL: Change to worktree directory FIRST:
  ```bash
  cd {backend_worktree}
  ```

  ALL file operations must happen in this directory.

  [Agent reads domain briefing]
  [Agent receives backend-specific prescriptive plan]
  [Agent implements features in isolation]

  Output: {backend_worktree}/.workflow/outputs/backend_results.json
  """
)

Task(
  subagent_type="implementation-agent-v1",
  description="Frontend implementation",
  prompt=f"""
  WORKTREE DIRECTORY: {frontend_worktree}

  CRITICAL: Change to worktree directory FIRST:
  ```bash
  cd {frontend_worktree}
  ```

  ALL file operations must happen in this directory.

  [Agent reads domain briefing]
  [Agent receives frontend-specific prescriptive plan]
  [Agent implements features in isolation]

  Output: {frontend_worktree}/.workflow/outputs/frontend_results.json
  """
)
```

**Phase 1C: Merge Results (Orchestrator, Sequential)**

```bash
# After all agents complete, orchestrator merges in dependency order
cd /main/repo/directory

# Merge backend first
git merge --no-ff feature/EPIC-007/backend -m "Merge backend implementation"

# Then frontend (can use backend's changes)
git merge --no-ff feature/EPIC-007/frontend -m "Merge frontend implementation"

# Check for conflicts
if git diff --check; then
  echo "✅ No merge conflicts"
else
  echo "⚠️ Merge conflicts detected - manual resolution required"
fi

# Cleanup worktrees after successful merge
python3 tools/worktree_manager/worktree_manager.py cleanup --epic EPIC-007
```

**Key Implementation Details:**

1. **Orchestrator creates worktrees** - Not agents
2. **Absolute paths provided** - Agents receive full path to their worktree
3. **First instruction: CD** - Agents change directory immediately
4. **Complete isolation** - No shared file access between agents
5. **Sequential merge** - Prevents conflicts, respects dependencies
6. **Automated cleanup** - Worktrees removed after successful merge

**Merge Strategy:**

Sequential merge with conflict detection:
```
database → backend → frontend → tests → docs
```

**GitHub Integration:**

- Creates epic issue with sub-issues for each parallel task
- Posts progress updates to GitHub as agents complete
- Links worktree branches to sub-issues

**Benefits:**
- **2-4x speedup** for large epics with separable concerns
- **Conflict-free** parallel work (isolated directories)
- **Observable** progress via GitHub Issues
- **Graceful fallback** to sequential if not viable

### 1.3 Validation System

**Files:**
- `tools/workflow_utilities_v6/comprehensive_v6_validation.py`
- `tools/workflow_utilities_v6/phase5c_build_and_lint_gate.py`
- `package.json` (npm scripts for validation)

**Validation Layers:**

**Layer 1: Architecture & Contracts**
```bash
npm run validate-architecture    # Boundary compliance
npm run validate-contracts        # JSON Schema validation
```

**Layer 2: Build & Lint (MANDATORY QUALITY GATE)**
```bash
npm run build:ts                  # TypeScript compilation
npm run lint:py                   # Python linting (Ruff)
npm run format:py:check           # Python formatting
```

**Phase 5C: Build Gate with Retry Loop**
```python
build_passed = False
max_attempts = 3
attempt = 0

while not build_passed and attempt < max_attempts:
    attempt += 1

    # Deploy build fixer agent
    Task(
        subagent_type="build-fixer-agent-v6",
        prompt=f"""
        Fix build/lint errors (attempt {attempt}/{max_attempts}).

        Errors:
        {build_errors}

        INSTRUCTIONS:
        - Fix ALL errors
        - Run npm run build:ts + npm run lint:py
        - Write results to phase5c_results_{attempt}.json
        """
    )

    # Check results
    results = read_json(f"phase5c_build_results_attempt_{attempt}.json")
    build_passed = (
        results.build_status == "passed" AND
        results.lint_status == "passed"
    )

if not build_passed:
    # STOP EXECUTION - manual intervention required
    raise QualityGateFailure("Build gate failed after max attempts")
```

**Layer 3: Testing (OPTIONAL for Tier 1)**
```bash
npm run test                      # Full test suite
npm run test:fast                 # Stop on first failure
```

**Key Principle: Explicit > Automatic**

All validation scripts are observable npm commands, not hidden hooks. Agents run these directly and report results.

**Note on Testing for Tier 1:**

The user explicitly stated: *"for most projects we actually do not want to bother with a 'testing' phase (since most tests are written to pass and not to actually identify issues - when written by coding agents)"*

**Implication:** Tier 1 should:
- ✅ Include build/lint validation (catches real issues)
- ✅ Include architecture/contract validation (enforces design)
- ❌ Skip comprehensive testing phase (tests written by agents often provide false confidence)
- ⚠️ Optionally run existing tests if project has them, but don't require agents to write tests

### 1.4 Post-Mortem & Knowledge Capture

**Files:**
- `tools/workflow_knowledge/post_mortem_analyzer.py`
- `tools/workflow_knowledge/knowledge_capture.py`
- `tools/workflow_knowledge/knowledge_query.py`

**Post-Mortem System Architecture:**

```
┌──────────────────────────────────────────────┐
│ Post-Mortem Orchestrator                     │
│ (main Claude Code session after workflow)    │
└──────────────────────────────────────────────┘
        ↓ Deploys 3 parallel analysis agents

┌──────────────────────┬──────────────────────┬──────────────────────┐
│ Code Quality Agent   │ Test Coverage Agent  │ Architecture Agent   │
│ - Complexity         │ - Coverage gaps      │ - Boundary compliance│
│ - Pattern adherence  │ - Test quality       │ - Health metrics     │
│ - Technical debt     │ - Missing tests      │ - Coupling analysis  │
└──────────────────────┴──────────────────────┴──────────────────────┘
        ↓ All agents write structured reports

┌──────────────────────────────────────────────┐
│ Knowledge Capture Service                    │
│ - Extracts metadata                          │
│ - Stores to docs/workflow_knowledge/         │
│ - Builds semantic index                      │
│ - Generates briefing update recommendations  │
└──────────────────────────────────────────────┘
```

**Post-Mortem Report Structure:**

```python
@dataclass
class PostMortemReport:
    epic_id: str
    completed_at: datetime

    # Code quality analysis
    code_quality: CodeQualityReport
    # - complexity_metrics (cyclomatic, cognitive)
    # - patterns_identified (design patterns used)
    # - technical_debt (issues to address)
    # - best_practices_followed

    # Test coverage analysis
    test_coverage: TestCoverageReport
    # - coverage_percentage
    # - missing_coverage (untested code paths)
    # - test_quality_score
    # - recommended_tests

    # Architecture analysis
    architecture: ArchitectureReport
    # - boundary_violations (if any)
    # - coupling_metrics
    # - architectural_health_score
    # - improvement_recommendations

    # Agent performance
    agent_performance: List[AgentPerformanceMetrics]
    # - agent_id, task_completion_time
    # - retry_count, success_rate

    # Challenges and resolutions
    challenges: List[Challenge]
    # - challenge_description
    # - resolution_strategy
    # - lessons_learned

    # Recommendations
    recommendations: Recommendations
    # - briefing_updates (suggested changes to domain briefings)
    # - pattern_additions (new patterns to add to library)
    # - workflow_improvements
```

**Knowledge Capture Workflow:**

1. **Extract Metadata** - Epic ID, branch, changed files, git stats
2. **Store to Repository** - `docs/workflow_knowledge/post-mortems/EPIC-007/`
3. **Build Semantic Index** - Enable natural language queries
4. **Queue Pattern Extraction** - Identify reusable patterns
5. **Generate Briefing Updates** - Suggest changes to domain briefings

**Knowledge Query System:**

```python
# Query past epics for relevant learnings
results = query_workflow_knowledge(
    query="How to handle async database operations with transaction safety?",
    max_results=5
)

# Returns:
# - EPIC-003: Database transaction patterns
# - EPIC-012: Async service layer best practices
# - EPIC-015: Error handling in async contexts
```

**Benefits:**
- **Continuous improvement** - Learn from every epic
- **Pattern accumulation** - Build institutional knowledge
- **Briefing evolution** - Domain briefings improve over time
- **Problem resolution** - Find solutions from similar past work

**For Tier 1:**

The full three-agent post-mortem is powerful but complex. A simplified version could:
- ✅ Single agent analyzes: What worked? What didn't? What to improve?
- ✅ Structured output: Challenges, resolutions, recommendations
- ✅ Store to knowledge repository
- ❌ Skip semantic indexing (overkill for most projects)
- ⚠️ Optional: Queue briefing update suggestions

### 1.5 Documentation System

**Files:**
- `tools/workflow_utilities_v6/phase5e_doc_data_collector.py`
- Freshness check system (integrated into Phase 0)

**V6 Documentation Philosophy: "Simple > Complex, Observable > Automatic"**

**Key Changes in V6 (Phase 6 Simplification):**

❌ **Removed:**
- Automatic documentation generation (complex, fragile)
- Update agents that rewrote entire docs
- Complex dependency tracking between docs

✅ **Kept:**
- Freshness check (detects stale docs)
- Manual updates (human reviews and updates)
- Frontmatter monitoring (tracks which files each doc cares about)

**Freshness Check System:**

```yaml
# Document frontmatter
---
title: "V6 Workflow Orchestration Reference"
last_updated: "2025-10-12"
git_hash: "a3f2b1c"
monitored_paths:
  - tools/workflow_utilities_v6/
  - .claude/commands/workflow_v6/
  - tools/mcp_servers/unified_v6_server.py
---
```

**How it Works:**

1. **Phase 0 Integration** - Lightweight freshness check runs during preflight
2. **Git Diff Detection** - Checks changed files since base branch
3. **Path Matching** - Compares against `monitored_paths` in frontmatter
4. **Non-Blocking Warnings** - Flags stale docs without halting workflow
5. **End-of-Workflow Reminder** - Prompts manual review after completion

**Manual Update Process:**

```bash
# 1. Review changes
git diff origin/dev HEAD -- tools/workflow_utilities_v6/

# 2. Update relevant sections
#    - TL;DR
#    - Code examples
#    - Tool descriptions

# 3. Update frontmatter
# last_updated: "2025-10-12"
# git_hash: "$(git rev-parse HEAD)"

# 4. Commit
git add docs/...
git commit -m "docs: Update for workflow changes"
```

**For Tier 1:**

Documentation automation is **NOT** recommended. The V6 approach is better:
- ✅ Freshness detection (optional, lightweight)
- ✅ Manual updates (human judgment > agent rewrites)
- ❌ Skip automatic doc generation
- ❌ Skip complex update agents

### 1.6 GitHub Integration

**Files:**
- `tools/github_integration/gh_cli_wrapper.py`
- `tools/github_integration/issue_sync_gh.py`
- `tools/github_integration/label_manager.py`

**Key Pattern: Non-Blocking, `gh` CLI-Based**

**Why `gh` CLI Instead of PyGithub:**

✅ **Advantages:**
- Uses existing `gh auth login` authentication (zero config)
- No token management or credential storage
- Simpler error handling (subprocess calls)
- Fewer dependencies (no PyGithub, requests, etc.)

**Core Operations:**

```python
# Create epic issue
issue = create_epic_issue(
    title="EPIC-007: Semantic Email Search",
    body=formatted_body,  # From spec.md + architecture.md
    domain="backend",
    priority="high"
)
# Returns: {"number": 123, "url": "https://..."}

# Create sub-issues for parallel work
sub_issue = create_sub_issue(
    parent_issue_number=123,
    title="Backend API Implementation",
    body=task_description,
    labels=["type:task", "domain:backend"]
)

# Sync status updates
sync_issue_status(
    issue_number=123,
    new_status="in-progress",
    comment="Status updated: backlog → in-progress"
)
# Updates labels: removes "status:planned", adds "status:in-progress"

# Post progress updates
post_comment(
    issue_number=123,
    comment="✅ Phase 5A complete: Backend services implemented"
)
```

**Label Taxonomy (24 labels):**

- **Status:** planned, in-progress, review, blocked, completed
- **Type:** epic, feature, task, sub-task
- **Domain:** backend, frontend, database, testing, docs
- **Priority:** critical, high, medium, low

**Non-Blocking Design:**

All GitHub operations catch exceptions and log failures without raising:

```python
try:
    issue_url = create_github_issue_from_epic(epic_id, epic_dir)
    if issue_url:
        print(f"✅ GitHub Issue: {issue_url}")
    else:
        print(f"⚠️ GitHub issue creation failed (see logs)")
except Exception as e:
    logger.error(f"GitHub sync error: {e}")
    # Workflow continues - local files are source of truth
```

**Bidirectional Sync:**

- **Local → GitHub:** Task creation/update triggers issue creation/update
- **GitHub → Local:** (Not fully implemented) Manual sync via command

**For Tier 1:**

GitHub integration is **highly recommended** - already built and working:
- ✅ Copy `tools/github_integration/` module to project
- ✅ Run one-time label initialization
- ✅ Add GitHub sync to task commands
- ✅ Keep non-blocking design (failures don't halt workflow)

---

## II. Tier 1 Workflow Enhancement Strategy

### 2.1 Core Principles for Tier 1

Based on V6 analysis and Tier 1 goals, the enhanced workflow should:

**✅ Include (High Value, Low Complexity):**

1. **Orchestrator Pattern** - Claude Code session coordinates agents
2. **Worktree Parallel Execution** - When file scopes don't overlap significantly
3. **Explicit Validation** - Build/lint/architecture checks (observable npm scripts)
4. **Lightweight Post-Mortem** - Single agent reviews execution
5. **GitHub Integration** - Epic → Issue → Sub-issues for parallel work

**❌ Exclude (Complexity > Value for Most Projects):**

1. **Comprehensive Testing Phase** - Tests written by agents provide false confidence
2. **Automatic Documentation** - Manual updates preferred (V6 lesson learned)
3. **Multi-Agent Post-Mortem** - Three parallel agents overkill
4. **Semantic Knowledge Index** - Nice-to-have, not essential
5. **Complex Workflow DAG** - Simpler linear execution sufficient

**⚠️ Optional (Project-Specific):**

1. **Graph-Server Integration** - If project has graph-server
2. **Pattern Library Queries** - If project has pattern library
3. **Contract/Schema Validation** - If project defines contracts in spec
4. **Compile/Type Checks** - Python: mypy, JavaScript: tsc

### 2.2 Recommended Tier 1 Workflow Command

**File:** `.claude/commands/execute-workflow.md`

**Workflow Phases (Simplified from V6):**

```
Phase 0: Preflight
├── Verify epic spec complete (spec.md, architecture.md, file-tasks.md)
├── Check git working directory clean
├── Detect parallel opportunities (optional)
└── Generate handoff briefing

Phase 1: Implementation
├── Deploy implementation agent(s)
│   ├── Sequential: Single agent follows file-tasks.md
│   └── Parallel: Multiple agents in isolated worktrees (if detected)
├── Agents write code per prescriptive plan
└── Agents write structured results (.workflow/outputs/phase1_results.json)

Phase 2: Validation
├── Build & Lint Gate (MANDATORY)
│   ├── npm run build:ts (if TypeScript)
│   ├── npm run lint:py (if Python)
│   ├── npm run validate-architecture (if project has boundaries)
│   └── Retry loop (max 3 attempts) with fixer agent
├── Contract Validation (OPTIONAL)
│   └── npm run validate-contracts (if spec defines contracts)
├── Run Existing Tests (OPTIONAL)
│   └── npm run test (if project has tests, but don't require writing new ones)
└── Block progression if build/lint fails

Phase 3: Documentation (OPTIONAL)
├── Freshness check (if project tracks docs)
├── Flag stale docs (non-blocking warning)
└── Manual update reminder (end of workflow)

Phase 4: Post-Mortem (LIGHTWEIGHT)
├── Deploy single analysis agent
├── Agent answers:
│   ├── What worked well?
│   ├── What challenges occurred?
│   ├── How were they resolved?
│   └── What should improve next time?
├── Write structured report (.workflow/post-mortem/EPIC-XXX.md)
└── Optional: Suggest briefing updates

Phase 5: Commit & Cleanup
├── Stage all changes
├── Generate commit message (from phase results)
├── Create commit
├── Cleanup worktrees (if parallel execution used)
└── Mark epic complete
```

**Orchestrator Prompt Template:**

```markdown
# .claude/commands/execute-workflow.md
---
description: "Execute Tier 1 workflow for epic implementation"
argument-hint: "<epic-id>"
allowed-tools: [Read, Write, Bash, Task]
---

## Tier 1 Workflow Execution

YOU are the ORCHESTRATOR. Agents are WORKERS. You coordinate, they execute.

### Step 1: Preflight Checks

Verify epic is ready:

```bash
EPIC_DIR=$(find .tasks -name "${ARGUMENTS}-*" -type d | head -1)
```

Check required files:
- [ ] spec.md exists and complete
- [ ] architecture.md exists
- [ ] implementation-details/file-tasks.md exists with prescriptive plan
- [ ] Git working directory clean: `git status --porcelain`

If any missing:
```
❌ Epic not ready for execution
Missing: [list files]
Run: /refine-epic ${ARGUMENTS}
```

### Step 2: Detect Parallel Opportunities (OPTIONAL)

Read `${EPIC_DIR}/implementation-details/file-tasks.md`.

Analyze for parallel execution:
- **Files to create/modify:** Count total files
- **Domains involved:** Identify domains (backend, frontend, database, docs)
- **File overlap:** Estimate shared files between tasks

**Criteria for parallel execution:**
- ✅ 5+ files across 2+ domains
- ✅ <30% file overlap
- ✅ Clear domain separation

If criteria met:
```
🔀 Parallel execution VIABLE
Files: 12 across 3 domains (backend, frontend, docs)
Overlap: 15% (2 shared files)
Strategy: Worktree isolation
```

If not met:
```
➡️ Sequential execution
Reason: [too few files | single domain | high overlap]
```

### Step 3A: Sequential Implementation

If parallel not viable:

Deploy single implementation agent:

```
Task(
  subagent_type="general-purpose",
  description="Implement epic ${ARGUMENTS}",
  prompt=f"""
  Implement epic ${ARGUMENTS} following the prescriptive plan.

  SPECIFICATION:
  [Read ${EPIC_DIR}/spec.md]

  ARCHITECTURE:
  [Read ${EPIC_DIR}/architecture.md]

  PRESCRIPTIVE PLAN:
  [Read ${EPIC_DIR}/implementation-details/file-tasks.md]

  INSTRUCTIONS:
  - Follow file-tasks.md exactly
  - Create/modify files as specified
  - Preserve existing functionality
  - Add error handling
  - Write clean, maintainable code

  OUTPUT:
  Write structured results to:
  .workflow/outputs/${ARGUMENTS}/phase1_results.json

  Format:
  {{
    "status": "success|partial|failed",
    "files_created": [...],
    "files_modified": [...],
    "issues_encountered": [...],
    "resolutions": [...]
  }}
  """
)
```

Wait for agent completion. Read results from `.workflow/outputs/${ARGUMENTS}/phase1_results.json`.

### Step 3B: Parallel Implementation (IF VIABLE)

If parallel execution viable:

**Step 3B.1: Create Worktrees**

```bash
cd tools/worktree_manager
python3 << 'EOF'
from worktree_manager import create_worktree_for_agent

# Create worktrees for each domain
backend_wt = create_worktree_for_agent("${ARGUMENTS}", "Backend Implementation")
frontend_wt = create_worktree_for_agent("${ARGUMENTS}", "Frontend Implementation")

print(f"Backend worktree: {backend_wt.path}")
print(f"Frontend worktree: {frontend_wt.path}")
EOF
```

**Step 3B.2: Deploy Parallel Agents**

Deploy agents in parallel (SINGLE message with multiple Task calls):

```
Task(
  subagent_type="general-purpose",
  description="Backend implementation",
  prompt=f"""
  [BACKEND BRIEFING...]
  Working directory: {backend_wt.path}
  Files to modify: [backend files only]
  Output: .workflow/outputs/${ARGUMENTS}/backend_results.json
  """
)

Task(
  subagent_type="general-purpose",
  description="Frontend implementation",
  prompt=f"""
  [FRONTEND BRIEFING...]
  Working directory: {frontend_wt.path}
  Files to modify: [frontend files only]
  Output: .workflow/outputs/${ARGUMENTS}/frontend_results.json
  """
)
```

**Step 3B.3: Merge Results**

After all agents complete:

```bash
# Merge in dependency order: database → backend → frontend
cd tools/worktree_manager
python3 << 'EOF'
from worktree_manager import merge_worktree_sequential

# Merge backend first
merge_worktree_sequential("${ARGUMENTS}-backend", "dev")

# Then frontend
merge_worktree_sequential("${ARGUMENTS}-frontend", "dev")

# Cleanup worktrees
cleanup_worktrees("${ARGUMENTS}")
EOF
```

Check for merge conflicts. If conflicts:
```
⚠️ Merge conflicts detected
Resolve manually in: [conflicted files]
```

### Step 4: Validation Phase

**Step 4.1: Build & Lint Gate (MANDATORY)**

Run validation:

```bash
# TypeScript (if exists)
if [ -f "tsconfig.json" ]; then
  npm run build:ts || BUILD_FAILED=1
fi

# Python (if exists)
if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
  npm run lint:py || LINT_FAILED=1
fi

# Architecture (if configured)
if [ -f "tools/architecture_validator.py" ]; then
  npm run validate-architecture || ARCH_FAILED=1
fi
```

If any failures:

Deploy fixer agent (max 3 attempts):

```
Task(
  subagent_type="general-purpose",
  description="Fix build/lint errors (attempt 1/3)",
  prompt=f"""
  Fix ALL build and lint errors.

  ERRORS:
  {error_output}

  INSTRUCTIONS:
  - Fix errors systematically
  - Re-run validation: npm run build:ts && npm run lint:py
  - Write results to: .workflow/outputs/${ARGUMENTS}/fix_attempt_1.json

  DO NOT mark task complete until ALL validations pass.
  """
)
```

Repeat until pass or max attempts exhausted.

If still failing after 3 attempts:
```
❌ WORKFLOW BLOCKED - Build/lint validation failed
Manual intervention required.
```

**Step 4.2: Contract Validation (OPTIONAL)**

If epic defines contracts (check frontmatter: `requires_json_schema: true`):

```bash
npm run validate-contracts
```

**Step 4.3: Run Existing Tests (OPTIONAL)**

If project has tests AND you want to run them:

```bash
npm run test
```

**Note:** DO NOT require agents to write tests. Tests written by agents often pass without finding real issues.

### Step 5: Documentation (OPTIONAL)

If project tracks documentation freshness:

```bash
# Check for stale docs (non-blocking)
python3 tools/check_doc_freshness.py --epic ${ARGUMENTS}
```

If stale docs found:
```
⚠️ Documentation may be stale:
- docs/reference/v6-workflow.md (last updated 2025-09-15)
- docs/architecture/system-design.md (last updated 2025-08-20)

Consider updating after workflow completion.
```

DO NOT auto-generate docs. Manual updates preferred.

### Step 6: Post-Mortem (LIGHTWEIGHT)

Deploy single analysis agent:

```
Task(
  subagent_type="general-purpose",
  description="Post-mortem analysis",
  prompt=f"""
  Analyze the workflow execution for ${ARGUMENTS}.

  REVIEW:
  - Implementation results: .workflow/outputs/${ARGUMENTS}/phase1_results.json
  - Validation results: .workflow/outputs/${ARGUMENTS}/validation_results.json
  - Git diff: git diff origin/dev HEAD

  ANSWER THESE QUESTIONS:

  1. What worked well?
     - Which parts of the implementation went smoothly?
     - Which prescriptive plans were clear and effective?
     - Which validation steps caught real issues?

  2. What challenges occurred?
     - What issues did the implementation agent encounter?
     - What validation errors occurred?
     - What required multiple attempts?

  3. How were challenges resolved?
     - What strategies worked for fixing issues?
     - What architectural decisions helped?
     - What could have been prevented?

  4. What should improve next time?
     - Which briefings need clarification?
     - Which prescriptive plans were unclear?
     - Which validation steps should be added/removed?

  OUTPUT:
  Write structured markdown report to:
  .workflow/post-mortem/${ARGUMENTS}.md

  Format:
  # Post-Mortem: ${ARGUMENTS}

  ## Summary
  [1-2 sentence overview]

  ## What Worked Well
  - [Item 1]
  - [Item 2]

  ## Challenges Encountered
  ### Challenge 1: [Title]
  - **Description:** ...
  - **Resolution:** ...
  - **Lesson:** ...

  ## Recommendations
  ### Briefing Updates
  - [Suggestion 1]

  ### Process Improvements
  - [Suggestion 1]
  """
)
```

Read post-mortem report. Display summary.

### Step 7: Commit & Cleanup

Stage all changes:

```bash
git add .
```

Generate commit message:

```bash
# Extract epic title from spec.md
EPIC_TITLE=$(grep "^# " ${EPIC_DIR}/spec.md | head -1 | sed 's/^# //')

# Get file counts from phase1_results.json
FILES_CREATED=$(jq -r '.files_created | length' .workflow/outputs/${ARGUMENTS}/phase1_results.json)
FILES_MODIFIED=$(jq -r '.files_modified | length' .workflow/outputs/${ARGUMENTS}/phase1_results.json)

# Create commit
cat > /tmp/commit_msg << EOF
feat(${ARGUMENTS}): ${EPIC_TITLE}

Implementation of ${ARGUMENTS}.

Files created: ${FILES_CREATED}
Files modified: ${FILES_MODIFIED}

Validation:
- Build: passed
- Lint: passed
- Architecture: passed

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
EOF

git commit -F /tmp/commit_msg
```

Cleanup worktrees (if parallel execution used):

```bash
if [ -d ".worktrees/${ARGUMENTS}-*" ]; then
  python3 tools/worktree_manager/cleanup.py --epic ${ARGUMENTS}
fi
```

Mark epic complete:

```bash
# Move epic to completed
mv ${EPIC_DIR} .tasks/completed/
```

### Completion Summary

Display:

```
✅ Workflow complete: ${ARGUMENTS}

Implementation:
- ${FILES_CREATED} files created
- ${FILES_MODIFIED} files modified
- Parallel execution: [yes/no]

Validation:
- Build: ✅ passed
- Lint: ✅ passed
- Architecture: ✅ passed

Post-Mortem: .workflow/post-mortem/${ARGUMENTS}.md

Next steps:
- Review post-mortem for insights
- Update documentation if flagged as stale
- Push to remote: git push origin dev
```
```

### 2.3 Integration with Tier 1 Task Management

**Tier 1 Already Has (from V6_TIER1_FINAL_IMPLEMENTATION_PLAN.md):**

✅ **Task CRUD** - Bash-based commands (task-create, task-get, task-update, task-list)
✅ **Epic Structure** - Hierarchical directories with spec.md, architecture.md
✅ **GitHub Integration** - Epic → Issue sync via `gh` CLI
✅ **Templates** - Jinja2 templates for tasks and epics

**Workflow Command Integrations:**

1. **Preflight:** Read epic files from `.tasks/backlog/EPIC-XXX/`
2. **Parallel Detection:** Parse `implementation-details/file-tasks.md`
3. **Worktrees:** Use `tools/worktree_manager/` (copy from email system)
4. **Validation:** Run npm scripts defined in project's `package.json`
5. **Post-Mortem:** Write to `.workflow/post-mortem/` directory
6. **Cleanup:** Update task status via `/task-update EPIC-XXX completed`

### 2.4 Worktree Manager for Tier 1

**Minimal Worktree Module (Copy from email_management_system):**

**Files to Copy:**

```bash
# From email_management_system
tools/worktree_manager/
├── __init__.py
├── worktree_manager.py       # Core operations
├── models.py                  # WorktreeMetadata dataclass
└── cleanup.py                 # Cleanup script
```

**Core Functions Needed:**

```python
# Create worktree
create_worktree_for_agent(epic_id: str, task_name: str, base_branch: str = "dev")

# List worktrees
list_worktrees(epic_id: Optional[str] = None, status: Optional[str] = None)

# Get metadata
get_worktree_metadata(worktree_name: str)

# Update status
update_worktree_status(worktree_name: str, status: str)

# Merge worktree
merge_worktree_sequential(worktree_name: str, target_branch: str)

# Cleanup
cleanup_worktrees(epic_id: str)
```

**No Changes Needed:** The worktree manager is project-agnostic and works for any Git repository.

### 2.5 Validation Scripts for Tier 1

**Most projects are Python-focused. Here's the Python-compatible validation structure:**

```json
// package.json (add to every Tier 1 project)
{
  "scripts": {
    "// ===== PYTHON LINTING =====": "",
    "lint:py": "ruff check .",
    "lint:py:fix": "ruff check --fix .",
    "format:py": "ruff format .",
    "format:py:check": "ruff format --check .",

    "// ===== PYTHON TYPE CHECKING =====": "",
    "typecheck:py": "mypy src/ --strict",
    "typecheck:py:report": "mypy src/ --html-report mypy-report/",

    "// ===== PYTHON TESTING (OPTIONAL) =====": "",
    "test:py": "pytest",
    "test:py:fast": "pytest -x",
    "test:py:coverage": "pytest --cov=src --cov-report=html",

    "// ===== ARCHITECTURE VALIDATION =====": "",
    "validate-architecture": "python3 tools/validate_architecture.py",
    "validate-contracts": "python3 tools/validate_contracts.py",

    "// ===== COMBINED VALIDATION =====": "",
    "validate-all": "npm run lint:py && npm run format:py:check && npm run typecheck:py && npm run validate-architecture",

    "// ===== TYPESCRIPT (if mixed project) =====": "",
    "build:ts": "tsc --noEmit",
    "lint:ts": "eslint src/"
  }
}
```

**Python Validation Phase (Phase 2):**

```bash
# MANDATORY: Linting + Formatting
npm run lint:py || LINT_FAILED=1
npm run format:py:check || FORMAT_FAILED=1

# MANDATORY: Type Checking (if using type hints)
if grep -r "from typing import" src/; then
  npm run typecheck:py || TYPE_FAILED=1
fi

# OPTIONAL: Architecture validation (if project has boundaries)
if [ -f "tools/validate_architecture.py" ]; then
  npm run validate-architecture || ARCH_FAILED=1
fi

# OPTIONAL: Contract validation (if spec defines contracts)
if [ -f "tools/validate_contracts.py" ]; then
  npm run validate-contracts || CONTRACT_FAILED=1
fi

# OPTIONAL: Run existing tests (don't require new tests)
if [ -d "tests/" ]; then
  npm run test:py || TEST_FAILED=1
fi
```

**Build/Lint Gate with Retry (Python Projects):**

```python
# Phase 2: Python validation with retry loop
max_attempts = 3
attempt = 0
validation_passed = False

while not validation_passed and attempt < max_attempts:
    attempt += 1

    # Run Python validation
    results = {
        "lint": subprocess.run(["npm", "run", "lint:py"]),
        "format": subprocess.run(["npm", "run", "format:py:check"]),
        "typecheck": subprocess.run(["npm", "run", "typecheck:py"])
    }

    failures = [k for k, v in results.items() if v.returncode != 0]

    if not failures:
        validation_passed = True
    else:
        # Deploy fixer agent
        Task(
          subagent_type="build-fixer-agent-v1",
          description=f"Fix validation errors (attempt {attempt}/3)",
          prompt=f"""
          Fix ALL Python validation errors.

          Failed checks: {', '.join(failures)}

          ERRORS:
          {get_error_output(results)}

          INSTRUCTIONS:
          - Fix linting errors: Run `npm run lint:py:fix` for auto-fixes
          - Fix formatting: Run `npm run format:py` to auto-format
          - Fix type errors: Add/fix type hints, resolve mypy complaints
          - Re-run validation: `npm run validate-all`
          - Write results to: .workflow/outputs/EPIC-007/fix_attempt_{attempt}.json

          DO NOT mark complete until ALL checks pass.
          """
        )

if not validation_passed:
    raise QualityGateFailure("Python validation failed after 3 attempts")
```

**Project Setup Checklist:**

- ✅ Add npm scripts to `package.json`
- ✅ Install Python tools:
  ```bash
  pip install ruff mypy pytest pytest-cov
  ```
- ✅ Configure mypy: Create `pyproject.toml` or `mypy.ini`
- ✅ Configure ruff: Create `ruff.toml` or add to `pyproject.toml`
- ⚠️ Architecture validator: Copy if project has architectural boundaries
- ⚠️ Contract validator: Copy if project uses JSON Schema contracts
- ⚠️ TypeScript: Only if mixed Python/TypeScript project

**Python Tool Configuration Examples:**

**pyproject.toml (Ruff + mypy):**

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

**For TypeScript Projects (Less Common):**

Replace Python scripts with:
```json
{
  "scripts": {
    "build:ts": "tsc --noEmit",
    "lint:ts": "eslint src/ --ext .ts,.tsx",
    "format:ts": "prettier --write src/",
    "format:ts:check": "prettier --check src/",
    "validate-all": "npm run build:ts && npm run lint:ts"
  }
}
```

### 2.6 Agent Creation and Briefing System (CRITICAL MISSING PIECE)

**This is the engine behind effective subagent deployment.**

The V6 workflow's power comes from **prescriptive plans + domain-specific briefings + phase-specific agent rules**. Agents are given:
1. **Phase-specific rules** - What they MUST/MUST NOT do based on workflow phase
2. **Domain-specific context** - Project patterns, architecture decisions, coding standards
3. **Prescriptive plan** - Exact files to create/modify with detailed instructions

#### 2.6.1 Directory Structure

```
.claude/
├── agent_definitions/                    # Phase-specific agent types
│   ├── implementation_agent_v1.md        # Implementation phase
│   ├── build_fixer_agent_v1.md           # Validation/fixing phase
│   ├── test_writer_agent_v1.md           # Testing phase (if used)
│   └── post_mortem_agent_v1.md           # Analysis phase
│
├── agent_briefings/                      # Domain-specific context
│   ├── backend_implementation.md         # Backend domain knowledge
│   ├── frontend_implementation.md        # Frontend domain knowledge
│   ├── database_implementation.md        # Database domain knowledge
│   └── project_architecture.md           # Project-wide patterns
│
└── commands/
    └── execute-workflow.md               # Orchestrator (composes agents + briefings)
```

#### 2.6.2 Agent Definition Example

**File:** `.claude/agent_definitions/implementation_agent_v1.md`

```markdown
---
agent_type: implementation-agent-v1
phase: implementation
description: Implements features following prescriptive plans
---

# Implementation Agent V1

YOU are an IMPLEMENTATION AGENT. Your role: Execute prescriptive plans exactly as specified.

## Core Responsibilities

- ✅ Follow file-tasks.md prescriptive plan exactly
- ✅ Create/modify files as specified
- ✅ Preserve existing functionality (no regressions)
- ✅ Add error handling for all operations
- ✅ Write clean, maintainable code following project patterns

## What You MUST Do

1. **Read Domain Briefing First** - Understand domain-specific patterns before coding
2. **Follow Prescriptive Plan** - file-tasks.md is your source of truth
3. **Preserve Existing Code** - Only change what's specified
4. **Add Error Handling** - All operations must handle failures gracefully
5. **Write Results** - Structured JSON output when complete

## What You MUST NOT Do

- ❌ **DO NOT write tests** - Testing phase handles this (if needed)
- ❌ **DO NOT write documentation** - Documentation updated manually
- ❌ **DO NOT refactor unrelated code** - Stay focused on the plan
- ❌ **DO NOT skip error handling** - Every operation needs error paths
- ❌ **DO NOT guess requirements** - If unclear, note in results JSON

## Output Format

Write structured results to `.workflow/outputs/{EPIC_ID}/implementation_results.json`:

```json
{
  "status": "success|partial|failed",
  "files_created": ["path/to/file1.py", ...],
  "files_modified": ["path/to/file2.py", ...],
  "issues_encountered": [
    {
      "description": "Type hint unclear for async function return",
      "file": "src/backend/service.py",
      "resolution": "Assumed -> Coroutine[None], please verify"
    }
  ],
  "clarifications_needed": [
    "Should EmailService.send() be async or sync?"
  ]
}
```

## Validation Before Completing

Before writing results JSON:

1. ✅ All files in file-tasks.md created/modified
2. ✅ No syntax errors (run `python -m py_compile <file>`)
3. ✅ No obvious linting errors (run `ruff check <file>`)
4. ✅ Error handling added to all operations
5. ✅ Existing tests still pass (if applicable)

DO NOT mark task complete until all checks pass.
```

#### 2.6.3 Domain Briefing Example

**File:** `.claude/agent_briefings/backend_implementation.md`

```markdown
---
domain: backend
updated: 2025-10-15
applies_to: [implementation-agent-v1, build-fixer-agent-v1]
---

# Backend Implementation Briefing

This briefing provides domain-specific patterns and rules for backend implementation in this project.

## Project Architecture

**Technology Stack:**
- Language: Python 3.11+
- Framework: FastAPI
- Database: PostgreSQL (via SQLAlchemy ORM)
- Async: asyncio + asyncpg

## File Structure

```
src/backend/
├── api/                    # API routes (FastAPI routers)
│   ├── email_routes.py     # /api/emails endpoints
│   └── auth_routes.py      # /api/auth endpoints
├── services/               # Business logic layer
│   ├── email_service.py    # EmailService class
│   └── auth_service.py     # AuthService class
├── models/                 # SQLAlchemy ORM models
│   ├── email.py            # Email model
│   └── user.py             # User model
└── schemas/                # Pydantic schemas (request/response)
    ├── email.py            # EmailCreate, EmailResponse
    └── user.py             # UserCreate, UserResponse
```

## Coding Patterns

### 1. Service Layer Pattern

ALL business logic goes in `services/` (not in API routes).

**Example:**

```python
# ✅ CORRECT: services/email_service.py
class EmailService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_email(self, email_data: EmailCreate) -> Email:
        """Create new email. Business logic here."""
        email = Email(**email_data.dict())
        self.db.add(email)
        await self.db.commit()
        return email

# ✅ CORRECT: api/email_routes.py
@router.post("/emails", response_model=EmailResponse)
async def create_email(
    email_data: EmailCreate,
    db: AsyncSession = Depends(get_db)
):
    """API route delegates to service."""
    service = EmailService(db)
    email = await service.create_email(email_data)
    return email

# ❌ WRONG: Business logic in API route
@router.post("/emails")
async def create_email(email_data: EmailCreate, db: AsyncSession):
    email = Email(**email_data.dict())  # ❌ Logic in route!
    db.add(email)
    await db.commit()
    return email
```

### 2. Error Handling

ALL service methods must handle errors with custom exceptions.

```python
# services/exceptions.py
class EmailNotFoundError(Exception):
    """Raised when email doesn't exist."""
    pass

# services/email_service.py
async def get_email(self, email_id: int) -> Email:
    email = await self.db.get(Email, email_id)
    if not email:
        raise EmailNotFoundError(f"Email {email_id} not found")
    return email

# api/email_routes.py
@router.get("/emails/{email_id}")
async def get_email(email_id: int, db: AsyncSession = Depends(get_db)):
    try:
        service = EmailService(db)
        return await service.get_email(email_id)
    except EmailNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### 3. Type Hints (MANDATORY)

ALL functions must have complete type hints.

```python
# ✅ CORRECT
async def get_email(self, email_id: int) -> Email:
    ...

async def list_emails(self, limit: int = 10) -> list[Email]:
    ...

# ❌ WRONG (missing type hints)
async def get_email(email_id):  # ❌ No types
    ...
```

## Common Mistakes to Avoid

1. ❌ **Business logic in API routes** - Always use service layer
2. ❌ **Missing error handling** - Every operation needs try/except
3. ❌ **Forgetting async/await** - Database operations are async
4. ❌ **Missing type hints** - mypy will fail validation
5. ❌ **Writing tests** - Implementation phase does NOT write tests

## Post-Implementation Checklist

Before writing results JSON:

- [ ] All business logic in `services/`
- [ ] All API routes delegate to services
- [ ] All functions have type hints
- [ ] All database operations are async
- [ ] Error handling added (custom exceptions + HTTPException)
- [ ] No tests written (per phase rules)
- [ ] Files match prescriptive plan exactly
```

#### 2.6.4 How Orchestrator Composes Agent + Briefing

**In the workflow command (orchestrator):**

```markdown
### Phase 1: Deploy Implementation Agents

For each domain (backend, frontend, database):

```python
Task(
  subagent_type="general-purpose",
  description="Backend implementation for EPIC-007",
  prompt=f"""
  YOU ARE: Implementation Agent V1

  {read_file(".claude/agent_definitions/implementation_agent_v1.md")}

  DOMAIN BRIEFING:

  {read_file(".claude/agent_briefings/backend_implementation.md")}

  PROJECT ARCHITECTURE:

  {read_file(".claude/agent_briefings/project_architecture.md")}

  WORKTREE DIRECTORY: {backend_worktree_path}

  CRITICAL: CD into worktree first:
  ```bash
  cd {backend_worktree_path}
  ```

  EPIC SPECIFICATION:

  {read_file(f".tasks/backlog/EPIC-007/spec.md")}

  ARCHITECTURE:

  {read_file(f".tasks/backlog/EPIC-007/architecture.md")}

  PRESCRIPTIVE PLAN (YOUR SOURCE OF TRUTH):

  {extract_backend_tasks_from_file_tasks_md()}

  FILES TO CREATE/MODIFY:
  - src/backend/services/email_service.py
  - src/backend/api/email_routes.py
  - src/backend/schemas/email.py

  OUTPUT FILE:
  .workflow/outputs/EPIC-007/backend_implementation_results.json

  BEGIN IMPLEMENTATION.
  """
)
```

#### 2.6.5 How Briefings Evolve (Post-Mortem Feedback)

**Post-mortem agent suggests briefing updates:**

```markdown
## Phase 4: Post-Mortem Analysis

Single agent reviews execution and suggests briefing updates:

```python
Task(
  subagent_type="general-purpose",
  description="Post-mortem analysis",
  prompt=f"""
  ...

  4. What should improve next time?
     - Which BRIEFINGS need clarification?
     - Which agent rules were unclear?
     - Which patterns should be added to domain briefings?

  OUTPUT SECTION:

  ### Briefing Update Recommendations

  **Backend Briefing (.claude/agent_briefings/backend_implementation.md):**
  - Add pattern: "When adding new endpoints, define Pydantic schemas first"
  - Clarify: "Service methods should raise custom exceptions, not HTTPException"

  **Implementation Agent Definition (.claude/agent_definitions/implementation_agent_v1.md):**
  - Add rule: "Run `ruff check --fix .` before marking task complete"
  - Emphasize: "If prescriptive plan mentions tests, skip and note in results"
  """
)
```

**Human reviews post-mortem and updates briefings accordingly.**

#### 2.6.6 Key Benefits of Agent/Briefing System

1. **Phase-Specific Rules** - Implementation agents don't write tests, fixer agents focus only on errors
2. **Domain-Specific Context** - Backend agents know FastAPI patterns, frontend agents know React patterns
3. **Continuous Improvement** - Post-mortems feed back into briefings
4. **Reusable Knowledge** - Briefings capture institutional knowledge
5. **Consistent Quality** - All agents follow same patterns

**This is the missing piece that makes the V6 workflow effective.**

### 2.7 GitHub Integration Enhancements

**Already Built (from Tier 1 Plan):**

✅ Epic → GitHub Issue creation
✅ Label taxonomy (24 labels)
✅ Non-blocking design

**Add for Parallel Execution:**

```python
# Create sub-issues for parallel tasks
def create_parallel_sub_issues(
    epic_id: str,
    parent_issue_number: int,
    parallel_plan: Dict
) -> List[int]:
    """Create GitHub sub-issues for parallel tasks."""
    sub_issue_numbers = []

    for domain, task_info in parallel_plan["tasks"].items():
        sub_issue = create_sub_issue(
            parent_issue_number=parent_issue_number,
            title=f"{epic_id}: {task_info['title']}",
            body=task_info['description'],
            labels=[f"type:task", f"domain:{domain}"]
        )
        sub_issue_numbers.append(sub_issue["number"])

    return sub_issue_numbers
```

**Progress Updates:**

```python
# Post progress updates to epic issue
def post_parallel_progress(
    epic_issue_number: int,
    completed_tasks: List[str],
    total_tasks: int
):
    """Post progress update to epic issue."""
    progress = len(completed_tasks) / total_tasks * 100
    comment = f"""
    🔄 Parallel Execution Progress: {progress:.0f}%

    Completed:
    {chr(10).join(f"- ✅ {task}" for task in completed_tasks)}

    Remaining: {total_tasks - len(completed_tasks)} tasks
    """
    post_comment(epic_issue_number, comment)
```

### 2.7 Post-Mortem Template

**File:** `.workflow/post-mortem/EPIC-XXX.md`

```markdown
---
epic_id: EPIC-XXX
title: [Epic Title]
completed_at: 2025-10-19
execution_mode: [sequential | parallel]
---

# Post-Mortem: EPIC-XXX

## Summary

[1-2 sentence overview of implementation]

## Execution Details

- **Files created:** X
- **Files modified:** Y
- **Execution mode:** [Sequential / Parallel (2 agents)]
- **Duration:** [Estimated time]
- **Validation attempts:** [1 / 2 / 3]

## What Worked Well

- **Clear prescriptive plan:** File-tasks.md specified exact changes, agents followed successfully
- **Effective validation:** Build/lint gate caught 2 issues before commit
- **Good separation:** Frontend/backend had minimal file overlap (12% shared)

## Challenges Encountered

### Challenge 1: Type Errors in API Integration

- **Description:** TypeScript compilation failed due to missing type definitions for new API endpoints
- **Resolution:** Added explicit type annotations in `src/api/types.ts`, imported in handlers
- **Lesson:** Prescriptive plans should include type definition requirements for TypeScript projects

### Challenge 2: Linting Violations (Import Order)

- **Description:** Ruff reported import order violations in 5 files
- **Resolution:** Agent ran `npm run lint:py:fix` to auto-fix
- **Lesson:** Include linting auto-fix step in agent briefings

## Recommendations

### Briefing Updates

**Backend Briefing:**
- Add explicit instruction: "When adding new API endpoints, define TypeScript types first"
- Include lint auto-fix step: "Run `npm run lint:py:fix` before final validation"

**Frontend Briefing:**
- Emphasize: "Check for unused imports after implementation (Ruff will flag)"

### Process Improvements

**Validation Phase:**
- Consider adding pre-validation check before agent starts (catches config issues early)
- Add retry limit reminder in agent briefing (avoid infinite fix loops)

**Parallel Execution:**
- Current threshold (5+ files, 2+ domains) works well
- Consider lowering file overlap threshold from 30% to 20% (more aggressive parallelization)

### Pattern Additions

**None identified** - Standard patterns worked well for this epic.

## Metrics

- **Validation pass rate:** 66% (passed on attempt 2/3)
- **File overlap (parallel):** 12% (2 shared files out of 17 total)
- **Build errors fixed:** 3 (TypeScript type issues)
- **Lint violations fixed:** 8 (import order, unused imports)

## Artifacts

- Implementation results: `.workflow/outputs/EPIC-XXX/phase1_results.json`
- Validation results: `.workflow/outputs/EPIC-XXX/validation_results.json`
- Git diff: `git diff origin/dev feature/EPIC-XXX/implementation`
```

---

## III. Implementation Roadmap

### 3.1 Week-by-Week Plan

**Week 1: Agent/Briefing System + Worktree Manager**

**Goal:** Create the foundational agent system (CRITICAL) and parallel execution capability

**Tasks:**
- [ ] Create `.claude/agent_definitions/` structure
  - [ ] `implementation_agent_v1.md` (core implementation rules)
  - [ ] `build_fixer_agent_v1.md` (validation fixing rules)
  - [ ] `post_mortem_agent_v1.md` (analysis rules)
- [ ] Create `.claude/agent_briefings/` templates
  - [ ] `backend_implementation.md` (example for Python/FastAPI)
  - [ ] `project_architecture.md` (project-wide patterns template)
- [ ] Copy `tools/worktree_manager/` from email_management_system
- [ ] Test worktree creation/cleanup in 2-3 projects
- [ ] Write parallel detection logic (read file-tasks.md, analyze domains/overlap)

**Deliverables:**
- Agent definition templates (3 files)
- Domain briefing templates (2 files)
- Working worktree manager (tested in 3 projects)
- Parallel detection script

**Week 2: Workflow Command (Sequential Path)**

**Goal:** Create basic workflow command with sequential execution

**Tasks:**
- [ ] Create `.claude/commands/execute-workflow.md`
- [ ] Implement Phase 0 (Preflight checks)
- [ ] Implement Phase 1 (Sequential implementation)
- [ ] Implement Phase 2 (Validation with retry loop)
- [ ] Implement Phase 5 (Commit & cleanup)
- [ ] Test end-to-end in 2 projects (one Python, one TypeScript)

**Deliverables:**
- Working sequential workflow command
- Tested in 2 diverse projects
- Documentation with examples

**Week 3: Workflow Command (Parallel Path)**

**Goal:** Add parallel execution to workflow command

**Tasks:**
- [ ] Integrate parallel detection into workflow
- [ ] Add worktree creation step (Phase 0)
- [ ] Add parallel agent deployment (Phase 1)
- [ ] Add sequential merge logic (Phase 1 post-processing)
- [ ] Add GitHub sub-issue creation (optional)
- [ ] Test parallel execution in 1 project with large epic (10+ files, 3+ domains)

**Deliverables:**
- Parallel execution working end-to-end
- GitHub sub-issues created for parallel tasks
- Performance comparison (parallel vs sequential timing)

**Week 4: Validation & Post-Mortem**

**Goal:** Add validation layers and post-mortem analysis

**Tasks:**
- [ ] Create validation scripts template:
  - `tools/validate_architecture.py` (optional)
  - `tools/validate_contracts.py` (optional)
- [ ] Add validation phase to workflow with retry loop
- [ ] Create post-mortem agent briefing
- [ ] Add post-mortem phase to workflow
- [ ] Test validation failure → fix → retry cycle
- [ ] Test post-mortem report generation

**Deliverables:**
- Validation scripts (copy-and-customize templates)
- Post-mortem agent integration
- Example post-mortem reports from 2 epics

**Week 5: Documentation & GitHub Enhancement**

**Goal:** Add optional documentation freshness and enhanced GitHub sync

**Tasks:**
- [ ] Create lightweight freshness check script (optional)
- [ ] Add GitHub progress updates for parallel execution
- [ ] Create installation script for workflow components:
  ```bash
  ~/install_tier1_workflow.sh <project-dir>
  ```
- [ ] Write comprehensive workflow documentation
- [ ] Create troubleshooting guide

**Deliverables:**
- Freshness check script (optional, project can skip)
- Enhanced GitHub integration
- Installation script (one-command setup)
- Complete workflow documentation

**Week 6: Rollout & Refinement**

**Goal:** Install in all active projects and gather feedback

**Tasks:**
- [ ] Install workflow in 5 diverse projects:
  - whisper_hotkeys (Python, small)
  - [project 2] (TypeScript, medium)
  - [project 3] (Mixed, large)
  - [project 4] (No graph-server)
  - [project 5] (With graph-server)
- [ ] Run 1-2 epics per project to validate
- [ ] Collect post-mortem reports
- [ ] Refine based on feedback
- [ ] Update documentation with learnings

**Deliverables:**
- Workflow installed in 5 projects
- 8-10 post-mortem reports analyzed
- Refinements applied based on real usage
- Final documentation published

### 3.2 File Structure for Tier 1 Enhanced Projects

```
<project>/
├── .tasks/
│   ├── backlog/
│   │   ├── EPIC-007-SemanticSearch/
│   │   │   ├── spec.md
│   │   │   ├── architecture.md
│   │   │   ├── task.md
│   │   │   ├── contracts/                  # Optional
│   │   │   │   └── api-contracts.yaml
│   │   │   └── implementation-details/
│   │   │       └── file-tasks.md           # Prescriptive plan
│   ├── current/
│   ├── completed/
│   └── templates/
│
├── .workflow/                              # NEW - Workflow execution artifacts
│   ├── outputs/
│   │   └── EPIC-007/
│   │       ├── phase1_results.json         # Implementation results
│   │       ├── validation_results.json     # Validation outcomes
│   │       └── fix_attempt_1.json          # Retry attempts
│   └── post-mortem/
│       └── EPIC-007.md                     # Post-mortem report
│
├── .worktrees/                             # NEW - Parallel execution
│   ├── .metadata/
│   │   └── EPIC-007-backend-a3f2.json      # Worktree metadata
│   ├── EPIC-007-backend-a3f2/              # Backend worktree
│   └── EPIC-007-frontend-b4e1/             # Frontend worktree
│
├── .claude/
│   ├── agent_definitions/                  # NEW - Phase-specific agent types
│   │   ├── implementation_agent_v1.md      # Implementation phase rules
│   │   ├── build_fixer_agent_v1.md         # Validation/fixing phase rules
│   │   └── post_mortem_agent_v1.md         # Analysis phase rules
│   │
│   ├── agent_briefings/                    # NEW - Domain-specific context
│   │   ├── backend_implementation.md       # Backend patterns & architecture
│   │   ├── frontend_implementation.md      # Frontend patterns (if applicable)
│   │   ├── database_implementation.md      # Database patterns (if applicable)
│   │   └── project_architecture.md         # Project-wide architectural rules
│   │
│   ├── commands/
│   │   ├── task-create.md
│   │   ├── spec-epic.md
│   │   └── execute-workflow.md             # NEW - Main workflow command
│   └── output-styles/
│       └── spec-architect.md
│
├── tools/
│   ├── worktree_manager/                   # NEW - Copied from email system
│   │   ├── worktree_manager.py
│   │   ├── models.py
│   │   └── cleanup.py
│   ├── github_integration/                 # Already exists (Tier 1 plan)
│   │   ├── gh_cli_wrapper.py
│   │   ├── issue_sync_gh.py
│   │   └── label_manager.py
│   ├── validate_architecture.py            # Optional
│   └── validate_contracts.py               # Optional
│
└── package.json                            # Python validation scripts
    {
      "scripts": {
        "lint:py": "ruff check .",
        "lint:py:fix": "ruff check --fix .",
        "format:py": "ruff format .",
        "format:py:check": "ruff format --check .",
        "typecheck:py": "mypy src/ --strict",
        "validate-architecture": "python3 tools/validate_architecture.py",
        "validate-all": "npm run lint:py && npm run format:py:check && npm run typecheck:py"
      }
    }
```

### 3.3 Installation Script Template

**File:** `install_tier1_workflow.sh`

```bash
#!/bin/bash
# Tier 1 Enhanced Workflow Installation
# Usage: ./install_tier1_workflow.sh <project-dir>

set -e

PROJECT_DIR="${1:-.}"
TEMPLATE_DIR="$HOME/v6-tier1-template"

echo "🚀 Installing Tier 1 Enhanced Workflow..."
echo "📂 Project: $PROJECT_DIR"
echo ""

# 1. Verify dependencies
echo "1️⃣ Verifying dependencies..."

# Check gh CLI
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi
echo "✅ GitHub CLI authenticated"

# Check git
if ! git -C "$PROJECT_DIR" status &>/dev/null; then
    echo "❌ Not a git repository: $PROJECT_DIR"
    exit 1
fi
echo "✅ Git repository detected"

# 2. Create directory structure
echo ""
echo "2️⃣ Creating directory structure..."
mkdir -p "$PROJECT_DIR/.workflow/"{outputs,post-mortem}
mkdir -p "$PROJECT_DIR/.worktrees/.metadata"
mkdir -p "$PROJECT_DIR/tools"
echo "✅ Directories created"

# 3. Copy worktree manager
echo ""
echo "3️⃣ Installing worktree manager..."
if [ ! -d "$TEMPLATE_DIR/tools/worktree_manager" ]; then
    echo "❌ Template not found: $TEMPLATE_DIR/tools/worktree_manager"
    echo "Please clone/copy the Tier 1 template first"
    exit 1
fi
cp -r "$TEMPLATE_DIR/tools/worktree_manager" "$PROJECT_DIR/tools/"
echo "✅ Worktree manager installed"

# 4. Copy workflow command
echo ""
echo "4️⃣ Installing workflow command..."
mkdir -p "$PROJECT_DIR/.claude/commands"
cp "$TEMPLATE_DIR/.claude/commands/execute-workflow.md" "$PROJECT_DIR/.claude/commands/"
echo "✅ Workflow command installed"

# 5. Copy validation scripts (optional)
echo ""
echo "5️⃣ Installing validation scripts (optional)..."
if [ -f "$TEMPLATE_DIR/tools/validate_architecture.py" ]; then
    cp "$TEMPLATE_DIR/tools/validate_architecture.py" "$PROJECT_DIR/tools/"
    echo "✅ Architecture validator installed"
fi
if [ -f "$TEMPLATE_DIR/tools/validate_contracts.py" ]; then
    cp "$TEMPLATE_DIR/tools/validate_contracts.py" "$PROJECT_DIR/tools/"
    echo "✅ Contract validator installed"
fi

# 6. Update package.json (if exists)
echo ""
echo "6️⃣ Updating package.json..."
if [ -f "$PROJECT_DIR/package.json" ]; then
    # Check if scripts section exists
    if ! grep -q '"scripts"' "$PROJECT_DIR/package.json"; then
        echo "⚠️ No scripts section in package.json"
        echo "Add validation scripts manually (see Tier 1 docs)"
    else
        echo "✅ package.json detected (manually add validation scripts)"
    fi
else
    echo "⚠️ No package.json found (create one if needed)"
fi

# 7. Create example epic structure
echo ""
echo "7️⃣ Creating example epic..."
EXAMPLE_DIR="$PROJECT_DIR/.tasks/backlog/EXAMPLE-001-WorkflowTest"
mkdir -p "$EXAMPLE_DIR"/{contracts,implementation-details}

cat > "$EXAMPLE_DIR/spec.md" << 'EOF'
---
epic_id: EXAMPLE-001
title: Workflow Test Epic
type: epic
status: backlog
priority: low
created: 2025-10-19
---

# EXAMPLE-001: Workflow Test Epic

This is an example epic created during installation. Delete it after testing.

## Problem Statement

Test the Tier 1 enhanced workflow system.

## Functional Requirements

- FR-1: Example requirement 1
- FR-2: Example requirement 2
EOF

cat > "$EXAMPLE_DIR/architecture.md" << 'EOF'
---
epic_id: EXAMPLE-001
type: architecture
---

# EXAMPLE-001: Architecture

## System Overview

Example architecture document.
EOF

cat > "$EXAMPLE_DIR/implementation-details/file-tasks.md" << 'EOF'
# Implementation Plan: EXAMPLE-001

## Files to Create

- `example.py` - Example Python file

## Files to Modify

- `README.md` - Add example section

## Implementation Steps

1. Create example.py with hello world function
2. Update README.md with usage example
EOF

echo "✅ Example epic created: $EXAMPLE_DIR"

# 8. Summary
echo ""
echo "✨ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add validation scripts to package.json (if applicable)"
echo "2. Test workflow: /execute-workflow EXAMPLE-001"
echo "3. Review post-mortem: .workflow/post-mortem/EXAMPLE-001.md"
echo "4. Delete example epic when done"
echo ""
echo "📚 Documentation:"
echo "- Workflow guide: .claude/commands/execute-workflow.md"
echo "- Worktree manager: tools/worktree_manager/README.md"
echo ""
echo "🎉 Happy workflow automation!"
```

---

## IV. Schema Validation Integration

### 4.1 Current State in V6

The V6 system includes **contract generation** from spec requirements:

**Process:**
1. Spec creation defines functional requirements
2. Contract generator creates JSON Schemas from requirements
3. Types generated: TypeScript (via `json-schema-to-typescript`), Python (via `datamodel-code-generator`)
4. Compilation verification ensures generated types are valid

**For Tier 1:**

The user asked: *"we add schema definition to our spec creation - but we have not actually integrated schema generation into the implementation phase, the question is if we could still use the schemas from the specs to somehow validate the implementation?"*

### 4.2 Schema Validation Strategy for Tier 1

**Two Approaches:**

**Approach 1: Define Schemas in Spec, Validate Manually**

During spec creation (Phase 0), humans define contracts in YAML:

```yaml
# contracts/api-contracts.yaml
UserLoginRequest:
  endpoint: POST /api/auth/login
  request:
    email: string
    password: string
    remember_me: boolean (optional)
  response_success:
    token: string
    user_id: string
  response_error:
    error: string
    message: string
```

During validation (Phase 2), **manually check** implementation matches:

```python
# Agent validates
"""
CHECK: src/api/auth.py endpoint signature matches spec
- Accepts email, password, remember_me
- Returns token and user_id on success
- Returns error and message on failure
"""
```

**Approach 2: Generate JSON Schemas, Validate at Runtime**

If project wants automated validation:

**Step 1: Convert YAML to JSON Schema (during spec creation)**

```python
# tools/generate_schemas.py
def yaml_to_json_schema(yaml_contracts: str) -> List[JSONSchema]:
    """Convert YAML contract definitions to JSON Schema."""
    # Parse YAML
    # Generate JSON Schema objects
    # Write to contracts/*.schema.json
```

**Step 2: Validate Requests/Responses at Runtime**

```python
# In actual implementation
from jsonschema import validate

def login(request: dict):
    # Validate request against schema
    with open("contracts/UserLoginRequest.schema.json") as f:
        schema = json.load(f)
    validate(instance=request, schema=schema)

    # Process request...
```

**Step 3: Validation Phase Checks Schemas Exist**

```bash
# Phase 2 validation
npm run validate-contracts

# Script checks:
# - All contracts/*.yaml have corresponding *.schema.json
# - All API endpoints reference a contract
# - Generated types compile successfully
```

### 4.3 Recommendation for Tier 1

**Start Simple (Approach 1):**

- ✅ Define contracts in spec.md (YAML blocks or structured text)
- ✅ Human review during implementation (agents check against spec)
- ✅ Validation phase asks: "Does implementation match spec contracts?"
- ❌ Skip automatic JSON Schema generation (complexity > value for most projects)

**Add Automation Later (Approach 2) if Needed:**

- ⚠️ Only for projects with:
  - Multiple APIs with strict contracts
  - External consumers requiring validation
  - Compliance requirements (e.g., healthcare, finance)

**Rationale:**

- Contract **definition** is valuable (documents API surface)
- Contract **validation** via JSON Schema is complex to set up correctly
- Most Tier 1 projects can rely on TypeScript/Python type systems
- Human review during spec creation catches most contract issues

**If You Want Automated Validation:**

Copy from email_management_system:
- `tools/spec_creation/contract_generator.py`
- `tools/workflow_utilities_v6/validate_contracts.py`
- Add to validation phase: `npm run validate-contracts`

---

## V. Critical Success Factors

### 5.1 What Makes V6 Workflow Successful

**Analyzed from email_management_system:**

1. **Orchestrator Pattern** - Claude Code session coordinates, doesn't execute
2. **Prescriptive Plans** - Phase 4 creates detailed file-tasks.md, agents follow
3. **Observable Execution** - All operations visible (no hidden magic)
4. **Explicit Validation** - npm scripts, not automatic hooks
5. **Non-Blocking GitHub** - Failures logged, workflow continues
6. **Post-Mortem Learning** - Captures what worked/didn't for improvement

### 5.2 Potential Pitfalls for Tier 1

**❌ Anti-Patterns to Avoid:**

1. **Over-Engineering** - Don't replicate full V6 complexity
2. **Hidden Complexity** - Keep all operations observable
3. **Automatic Everything** - Manual review > agent-generated docs/tests
4. **Rigid Parallelization** - Graceful fallback to sequential
5. **Testing Theater** - Tests written by agents often don't find real issues

**✅ Keep Simple:**

1. **Start Sequential** - Add parallel execution only when beneficial
2. **Explicit Validation** - Observable npm scripts, not mysterious hooks
3. **Lightweight Post-Mortem** - Single agent, focused questions
4. **Manual Documentation** - Freshness checks OK, auto-generation NO
5. **Non-Blocking GitHub** - Failures don't halt workflow

### 5.3 Metrics for Success

**Track These for Each Workflow Execution:**

- **Execution Mode:** Sequential / Parallel (X agents)
- **Files Changed:** Created / Modified counts
- **Validation Attempts:** 1 / 2 / 3 (build/lint retry count)
- **Parallel Speedup:** Duration comparison (if parallel used)
- **GitHub Sync:** Success / Failed (non-blocking)
- **Post-Mortem Quality:** Actionable recommendations count

**Quarterly Review:**

- Analyze 10-20 post-mortems
- Identify common issues
- Update briefings based on learnings
- Refine parallel detection criteria
- Adjust validation retry limits

---

## VI. Conclusions & Recommendations

### 6.1 Summary of Findings

The V6 workflow from email_management_system is a **production-grade, sophisticated system** with proven value. Key components worth porting to Tier 1:

**High Value, Portable (MUST HAVE):**
1. ✅ **Orchestrator pattern** - Claude Code coordinates agents
2. ✅ **Agent/briefing system** - Phase-specific rules + domain-specific context (CRITICAL ENGINE)
3. ✅ **Worktree parallel execution** - 2-4x speedup for large epics
4. ✅ **Python validation** - Ruff, mypy, pytest (not TypeScript-focused)
5. ✅ **Lightweight post-mortem** - Single agent review
6. ✅ **GitHub integration** - Already built, non-blocking

**Low Value or Too Complex:**
1. ❌ **Multi-agent post-mortem** - Three parallel agents overkill
2. ❌ **Semantic knowledge index** - Nice-to-have, not essential
3. ❌ **Automatic documentation** - Manual updates preferred
4. ❌ **Complex testing phase** - Agent-written tests provide false confidence
5. ❌ **Full V6 workflow DAG** - Simpler linear execution sufficient

### 6.2 Primary Recommendation

**Implement a simplified workflow command for Tier 1 with:**

**Phase 0: Preflight** (30 seconds)
- Verify epic spec complete
- Check git clean
- Detect parallel opportunities

**Phase 1: Implementation** (5-30 minutes)
- Sequential: Single agent follows file-tasks.md
- Parallel: Multiple agents in isolated worktrees (if viable)

**Phase 2: Validation** (2-5 minutes)
- Build/lint gate (mandatory, max 3 retry attempts)
- Architecture/contract validation (optional)
- Run existing tests (optional, don't require writing new tests)

**Phase 3: Post-Mortem** (2-3 minutes)
- Single agent answers: What worked? What didn't? What to improve?
- Structured markdown report

**Phase 4: Commit & Cleanup** (1 minute)
- Stage changes, generate commit message
- Cleanup worktrees (if used)
- Mark epic complete

**Total Duration:** ~10-40 minutes per epic (depending on size and parallel execution)

### 6.3 Implementation Timeline

**6 Weeks to Production Rollout:**

- **Week 1:** Worktree manager + parallel detection
- **Week 2:** Sequential workflow path
- **Week 3:** Parallel workflow path
- **Week 4:** Validation + post-mortem
- **Week 5:** GitHub enhancement + installation script
- **Week 6:** Rollout to 5 projects + refinement

**Effort:** ~2-3 hours/day over 6 weeks = 60-90 hours total

**ROI:** After initial setup, each project gets:
- 2-4x speedup for large epics (parallel execution)
- Consistent validation (fewer broken commits)
- Institutional learning (post-mortem knowledge)
- GitHub visibility (stakeholder transparency)

### 6.4 Next Steps

**Immediate Actions (Next 7 Days):**

1. **Validate this assessment** - Review with team/users
2. **Prototype worktree manager** - Copy from email system, test in 1 project
3. **Draft workflow command** - Write Phase 0 + Phase 1 (sequential path)
4. **Test basic flow** - Create example epic, run workflow end-to-end
5. **Gather feedback** - Identify rough edges, refine approach

**If Validated, Execute 6-Week Roadmap**

---

## VII. Appendices

### Appendix A: File References from email_management_system

**Workflow Orchestration:**
- `.claude/commands/workflow_v6/w-workflow-v6-mcp.md` - Main workflow command
- `tools/workflow_utilities_v6/interactive_workflow/parallel_execution_manager.py` - Parallel execution logic

**Worktree Management:**
- `tools/worktree_manager/worktree_manager.py` - Core worktree operations
- `tools/worktree_manager/models.py` - Metadata structures

**Validation:**
- `tools/workflow_utilities_v6/comprehensive_v6_validation.py` - Validation test suite
- `tools/workflow_utilities_v6/phase5c_build_and_lint_gate.py` - Build gate with retry
- `package.json` - npm validation scripts

**Post-Mortem:**
- `tools/workflow_knowledge/post_mortem_analyzer.py` - Three-agent analysis orchestrator
- `tools/workflow_knowledge/knowledge_capture.py` - Knowledge repository service
- `tools/workflow_knowledge/knowledge_query.py` - Semantic query interface

**GitHub Integration:**
- `tools/github_integration/gh_cli_wrapper.py` - gh CLI operations
- `tools/github_integration/issue_sync_gh.py` - Bidirectional sync
- `tools/github_integration/label_manager.py` - Label taxonomy

### Appendix B: Comparison Matrix

| Feature | V6 (email_management_system) | Tier 1 (Recommended) | Rationale |
|---------|------------------------------|----------------------|-----------|
| **Orchestration** | Claude + MCP + DAG | Claude + Commands | Simpler, same pattern |
| **Parallel Execution** | Fork-join with worktrees | Worktrees (same) | Copy as-is |
| **Phases** | 0-7 (8 phases) | 0-4 (5 phases) | Fewer phases, same value |
| **Validation** | Architecture + Build + Lint + Test + Contract | Build + Lint + Architecture (optional) | Skip testing phase |
| **Post-Mortem** | 3 parallel agents | 1 agent | Simpler, sufficient |
| **Documentation** | Freshness check (manual update) | Same | Already simplified in V6 |
| **GitHub Sync** | Epic → Issue + Sub-issues | Same | Copy as-is |
| **Knowledge Capture** | Semantic index + YAML metadata | Markdown reports only | Skip semantic index |
| **Contract Validation** | JSON Schema generation | Manual or optional | Start simple |
| **Testing** | Comprehensive (Phase 5D) | Run existing only | Don't require new tests |
| **Lines of Code** | ~10,000 (V6 system) | ~1,500 (estimated) | 85% reduction |
| **Setup Time** | 1 week (complex) | 1-2 hours (simple) | Much faster |
| **Maintenance** | 4-8 hrs/month | ~15 min/month | Much lower |

### Appendix C: Tier 1 Enhanced vs Tier 1 Basic

| Feature | Tier 1 Basic (Current Plan) | Tier 1 Enhanced (This Assessment) |
|---------|------------------------------|-----------------------------------|
| **Task CRUD** | ✅ Bash commands | ✅ Same |
| **Epic Specs** | ✅ Interactive creation | ✅ Same |
| **GitHub Sync** | ✅ Epic → Issue | ✅ Epic → Issue + Sub-issues (parallel) |
| **Workflow Execution** | ❌ Manual | ✅ Automated workflow command |
| **Parallel Execution** | ❌ None | ✅ Worktree-based parallel agents |
| **Validation** | ❌ Manual | ✅ Build/lint gate with retry |
| **Post-Mortem** | ❌ None | ✅ Lightweight single-agent analysis |
| **Knowledge Capture** | ❌ None | ✅ Structured markdown reports |
| **Complexity** | Very Low | Low-Medium |
| **Setup Time** | 1-2 hours | 3-4 hours (includes workflow setup) |
| **Value Add** | High (task management) | Very High (full workflow automation) |

---

**End of Assessment**

This document provides a comprehensive analysis of the V6 workflow architecture and a detailed strategy for porting essential components to Tier 1. The recommended approach balances value (workflow automation, parallel execution, validation) with simplicity (fewer phases, lightweight post-mortem, optional features).

**Key Takeaways:**

1. **Agent/Briefing System is CRITICAL** - This is the engine that makes V6 effective. Without it, agents won't know:
   - What they MUST NOT do in each phase (e.g., implementation agents don't write tests)
   - Project-specific patterns (e.g., service layer architecture, error handling)
   - Domain-specific context (e.g., FastAPI patterns, async/await requirements)

2. **Python-First Validation** - Most projects use Python (not TypeScript), so validation must support:
   - Ruff (linting + formatting)
   - mypy (type checking)
   - pytest (testing, optional)

3. **Worktree Implementation** - Simple and elegant:
   - Orchestrator creates worktrees BEFORE deploying agents
   - Agents receive absolute path and CD into worktree directory
   - All work happens in isolation
   - Orchestrator merges sequentially after agents complete

4. **Start Simple, Iterate** - Begin with simplified workflow command (Phases 0-4), test in 2-3 projects, gather feedback via post-mortems, then roll out. Add optional features (contract validation, semantic indexing) only if specific projects need them.
