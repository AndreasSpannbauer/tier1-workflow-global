# Workflow Integration Guide

**Last Updated:** 2025-10-19
**Status:** Production Ready
**Location:** `~/tier1_workflow_global/implementation/`

---

## Overview

The Tier 1 workflow command (`/execute-workflow`) automates the complete implementation lifecycle for prescriptive epics:

1. **Preflight checks** - Verify epic readiness and clean git state
2. **Implementation** - Deploy agents to execute prescriptive plans
3. **Validation** - Automated linting, type checking, and testing
4. **Commit & Cleanup** - Create properly formatted commit and move epic to completed/

**Key Benefits:**
- Hands-off execution (no manual intervention required)
- Automatic validation with retry logic
- Conventional commit formatting with metadata
- Structured result artifacts for audit trail
- Support for both sequential and parallel execution paths

---

## Prerequisites

### 1. Task Directory Structure

Your project must have a `.tasks/` directory with the following structure:

```
.tasks/
├── backlog/
│   └── EPIC-XXX-*/
│       ├── spec.md                       # Epic specification
│       ├── architecture.md                # Architecture design
│       └── implementation-details/
│           └── file-tasks.md              # Prescriptive plan
└── completed/
    └── EPIC-XXX-*/                        # Moved here after workflow completes
```

**How to create epics:**
- Run `/spec-epic` to create a new epic with AI assistance
- Run `/refine-epic EPIC-XXX` to generate architecture.md and file-tasks.md

### 2. Package.json Validation Scripts

Your `package.json` must include validation commands:

```json
{
  "scripts": {
    "validate:python": "ruff check src/ && mypy src/",
    "validate:typescript": "npm run lint && npm run type-check",
    "validate": "npm run validate:python && npm run validate:typescript"
  }
}
```

**Python projects only:**
```json
{
  "scripts": {
    "validate": "ruff check src/ && mypy src/"
  }
}
```

**TypeScript projects only:**
```json
{
  "scripts": {
    "validate": "npm run lint && tsc --noEmit"
  }
}
```

### 3. Python Tools Installed

For Python projects, install validation tools:

```bash
pip install ruff mypy

# Or add to requirements.txt / pyproject.toml
```

**Ruff configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 4. Agent Definitions and Briefings

The workflow command requires agent definitions and briefings to be present:

**Agent Definitions** (`.claude/agent_definitions/`):
- `implementation_agent_v1.md` - Main implementation agent
- `build_fixer_agent_v1.md` - Validation fixer agent
- `post_mortem_agent_v1.md` - Post-mortem analysis (optional)

**Agent Briefings** (`.claude/agent_briefings/`):
- `backend_implementation.md` - Backend-specific patterns
- `project_architecture.md` - Project-specific conventions

These are provided in the `tier1_workflow_global/implementation/` directory and must be copied to your project (see Installation below).

### 5. Clean Git Working Directory

The workflow requires a clean git state to execute:

```bash
# Verify git status is clean
git status

# Should show:
# "nothing to commit, working tree clean"
```

If you have uncommitted changes, commit or stash them before running the workflow.

---

## Installation

### Step 1: Copy Workflow Command

Copy the workflow command to your global `.claude/commands/` directory:

```bash
# Create commands directory if not exists
mkdir -p ~/.claude/commands

# Copy workflow command
cp ~/tier1_workflow_global/implementation/.claude/commands/execute-workflow.md \
   ~/.claude/commands/

# Verify
ls ~/.claude/commands/execute-workflow.md
```

**Note:** This makes `/execute-workflow` available across ALL projects.

### Step 2: Copy Agent Definitions (Global)

Copy agent definitions to your global `.claude/agent_definitions/` directory:

```bash
# Create directory if not exists
mkdir -p ~/.claude/agent_definitions

# Copy all agent definitions
cp ~/tier1_workflow_global/implementation/agent_definitions/*.md \
   ~/.claude/agent_definitions/

# Verify
ls ~/.claude/agent_definitions/
# Should show:
# - implementation_agent_v1.md
# - build_fixer_agent_v1.md
# - post_mortem_agent_v1.md
```

### Step 3: Copy Agent Briefings (Project-Specific)

Copy agent briefings to your **project's** `.claude/agent_briefings/` directory:

```bash
# Navigate to your project
cd /path/to/your/project

# Create directory
mkdir -p .claude/agent_briefings

# Copy briefing templates
cp ~/tier1_workflow_global/implementation/agent_briefings/*.md \
   .claude/agent_briefings/

# Verify
ls .claude/agent_briefings/
# Should show:
# - backend_implementation.md
# - project_architecture.md
```

### Step 4: Customize Briefings for Your Project

Edit `.claude/agent_briefings/backend_implementation.md` to match your project:

**Update Technology Stack:**
```markdown
**Technology Stack:**
- Language: Python 3.11+ (or Python 3.9+, Node.js 18+, etc.)
- Framework: FastAPI (or Flask, Django, Express, NestJS, etc.)
- Database: PostgreSQL (or MySQL, MongoDB, etc.)
- Async: asyncio + asyncpg (or sync, promises, etc.)
```

**Update File Structure:**
```markdown
src/backend/         # Or backend/, server/, api/, etc.
├── api/             # Or routes/, controllers/, handlers/
├── services/        # Or use_cases/, domain/, business_logic/
├── models/          # Or entities/, db/, schemas/
└── schemas/         # Or dto/, types/, interfaces/
```

**Update Coding Patterns:**
- Add project-specific error handling
- Document naming conventions
- Include domain-specific validation rules

**Update Project Architecture Briefing:**

Edit `.claude/agent_briefings/project_architecture.md`:

```markdown
# Project Architecture Briefing

## Technology Stack
[List your actual stack]

## Design Principles
[Document your architectural patterns]

## Directory Structure
[Show your actual project structure]

## Conventions
[Document your team's conventions]
```

---

## Usage

### Basic Workflow

**Step 1: Create Epic**
```bash
# Start Claude Code session
claude

# Create epic specification
/spec-epic
```

Claude will guide you through creating a detailed epic specification. You'll receive an epic ID like `EPIC-042`.

**Step 2: Refine Epic**
```bash
# Generate architecture and implementation plan
/refine-epic EPIC-042
```

Claude will:
- Analyze your spec.md
- Generate architecture.md (design decisions)
- Generate file-tasks.md (prescriptive implementation plan)

**Step 3: Review Implementation Plan**
```bash
# Review the prescriptive plan
cat .tasks/backlog/EPIC-042-*/implementation-details/file-tasks.md
```

Verify:
- File paths are correct
- Instructions are clear
- No critical files missing

**Step 4: Execute Workflow**
```bash
# Run automated workflow
/execute-workflow EPIC-042
```

The workflow will:
1. Run preflight checks
2. Deploy implementation agent
3. Validate code with automatic fixes
4. Create git commit
5. Move epic to completed/

**Step 5: Review and Push**
```bash
# Review the commit
git log -1 -p

# Check result artifacts
cat .workflow/outputs/EPIC-042/phase1_results.json
cat .workflow/outputs/EPIC-042/validation_results.json

# Push to remote
git push origin main
```

### Advanced Usage

**Parallel Execution (Automatic Detection):**

If your epic has 5+ files across 2+ domains with <30% overlap, the workflow will automatically use parallel execution:

```bash
/execute-workflow EPIC-042

# Output:
# 🔀 Parallel execution VIABLE
# Reason: 14 files across 4 domains with 0.0% overlap
#
# Domains for parallel execution:
#   - backend: Backend API implementation (5 files)
#   - frontend: Frontend UI implementation (5 files)
#   - database: Database schema and migrations (2 files)
#   - docs: Documentation updates (2 files)
#
# Deploying parallel agents...
```

**Sequential Execution (Default):**

For smaller epics or single-domain work, sequential execution is used:

```bash
/execute-workflow EPIC-042

# Output:
# ➡️ Sequential execution
# Reason: 3 files in 1 domain (backend only)
#
# Deploying implementation agent...
```

---

## Expected Workflow

### Phase 0: Preflight (30 seconds)

**What happens:**
1. Locate epic directory in `.tasks/backlog/`
2. Verify spec.md, architecture.md, file-tasks.md exist
3. Check git working directory is clean
4. Run parallel detection analysis
5. Determine execution path (sequential or parallel)

**Expected output:**
```
🚀 Phase 0: Preflight

✅ Epic ready: EPIC-042
   - spec.md found
   - architecture.md found
   - file-tasks.md found

✅ Git working directory clean

🔀 Analyzing parallel opportunities...
   - File count: 14
   - Domain count: 4 (backend, frontend, database, docs)
   - File overlap: 0.0%

✅ Parallel execution VIABLE
```

### Phase 1: Implementation (5-30 minutes)

**What happens:**

**Sequential Path:**
1. Read domain briefings and architecture
2. Read prescriptive plan (file-tasks.md)
3. Deploy single implementation agent
4. Agent creates/modifies files per plan
5. Agent writes results JSON
6. Verify all files created/modified

**Parallel Path:**
1. Create temporary worktrees (one per domain)
2. Deploy parallel agents (one per domain)
3. Each agent works on domain-specific files independently
4. Agents write results JSON
5. Merge changes back to main branch
6. Clean up worktrees

**Expected output:**
```
🔨 Phase 1: Implementation

Deploying implementation agent...
Agent: implementation-agent-v1
Briefings: backend_implementation.md, project_architecture.md

[Agent works...]

Files created: 3
  - src/backend/services/email_service.py
  - src/backend/api/email_routes.py
  - src/backend/schemas/email.py

Files modified: 2
  - src/backend/api/__init__.py
  - src/backend/main.py

✅ Phase 1 Complete
Results: .workflow/outputs/EPIC-042/phase1_results.json
```

### Phase 2: Validation (2-5 minutes)

**What happens:**
1. Run validation commands from package.json
2. Capture stdout/stderr
3. If validation fails:
   - Deploy build_fixer_agent_v1
   - Agent analyzes errors
   - Agent applies fixes
   - Re-run validation
   - Retry up to 3 times
4. If still failing after 3 attempts, abort with error

**Expected output (Success):**
```
🔍 Phase 2: Validation

Running validation: npm run validate
Command: ruff check src/ && mypy src/

✅ Python linting passed (0 errors)
✅ Type checking passed (0 errors)

✅ Validation passed

Results: .workflow/outputs/EPIC-042/validation_results.json
```

**Expected output (Failure with Auto-Fix):**
```
🔍 Phase 2: Validation

Running validation: npm run validate
Command: ruff check src/ && mypy src/

❌ Validation failed (attempt 1/3)

Errors found:
  - src/backend/services/email_service.py:42: Missing type hint for 'db' parameter
  - src/backend/api/email_routes.py:18: Unused import 'HTTPException'

Deploying build_fixer_agent_v1...
[Agent analyzes and fixes errors...]

Re-running validation...
✅ Validation passed

Results: .workflow/outputs/EPIC-042/validation_results.json
```

### Phase 5: Commit & Cleanup (1 minute)

**What happens:**
1. Stage all modified/created files
2. Create conventional commit with:
   - Type (feat, fix, refactor, etc.)
   - Epic ID
   - Short description
   - Body with file summary
   - Footer with metadata
3. Move epic directory from `backlog/` to `completed/`
4. Clean up `.workflow/outputs/EPIC-042/` artifacts

**Expected output:**
```
📦 Phase 5: Commit & Cleanup

Staging files:
  - src/backend/services/email_service.py
  - src/backend/api/email_routes.py
  - src/backend/schemas/email.py
  - src/backend/api/__init__.py
  - src/backend/main.py

Creating commit...

Commit message:
────────────────────────────────
feat(EPIC-042): Add email validation to user registration

Implemented email validation service with custom exceptions
and integration into auth routes.

Files:
- Created: 3 files
- Modified: 2 files

🤖 Generated with Claude Code
https://claude.com/claude-code

Co-Authored-By: Claude <noreply@anthropic.com>
────────────────────────────────

✅ Commit created: abc123d

Moving epic to completed/...
✅ Epic moved: EPIC-042-add-email-validation

✅ Workflow Complete: EPIC-042
```

---

## Output Artifacts

### Phase 1 Results JSON

**Location:** `.workflow/outputs/EPIC-XXX/phase1_results.json`

**Content:**
```json
{
  "status": "success",
  "epic_id": "EPIC-042",
  "agent_type": "implementation-agent-v1",
  "execution_mode": "sequential",
  "files_created": [
    "src/backend/services/email_service.py",
    "src/backend/api/email_routes.py",
    "src/backend/schemas/email.py"
  ],
  "files_modified": [
    "src/backend/api/__init__.py",
    "src/backend/main.py"
  ],
  "issues_encountered": [
    {
      "description": "Type hint unclear for async function return",
      "file": "src/backend/services/email_service.py",
      "resolution": "Assumed -> Coroutine[None], please verify"
    }
  ],
  "clarifications_needed": [],
  "completion_timestamp": "2025-10-19T14:30:00Z"
}
```

### Validation Results JSON

**Location:** `.workflow/outputs/EPIC-XXX/validation_results.json`

**Content:**
```json
{
  "status": "success",
  "epic_id": "EPIC-042",
  "validation_attempts": 1,
  "final_result": "passed",
  "errors_found": [],
  "auto_fixes_applied": false,
  "validation_command": "ruff check src/ && mypy src/",
  "stdout": "All checks passed!",
  "stderr": "",
  "completion_timestamp": "2025-10-19T14:35:00Z"
}
```

### Git Commit

**Format:** Conventional Commits with metadata

**Example:**
```
commit abc123def456789
Author: Your Name <your.email@example.com>
Date:   Sat Oct 19 14:35:00 2025 +0200

    feat(EPIC-042): Add email validation to user registration

    Implemented email validation service with custom exceptions
    and integration into auth routes.

    Files:
    - Created: 3 files
    - Modified: 2 files

    🤖 Generated with Claude Code
    https://claude.com/claude-code

    Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Troubleshooting

For detailed troubleshooting, see [WORKFLOW_TROUBLESHOOTING.md](./WORKFLOW_TROUBLESHOOTING.md).

**Quick checks:**

**Epic not ready:**
```bash
# Verify epic structure
ls .tasks/backlog/EPIC-042-*/
# Should show: spec.md, architecture.md, implementation-details/

# If missing, run:
/refine-epic EPIC-042
```

**Git not clean:**
```bash
git status
# If uncommitted changes:
git add .
git commit -m "WIP: Prepare for workflow"
```

**Validation errors:**
```bash
# Check validation logs
cat .workflow/outputs/EPIC-042/validation_errors.log

# Run validation manually
npm run validate
```

---

## Next Steps

1. Read [WORKFLOW_EXAMPLE.md](./WORKFLOW_EXAMPLE.md) for a complete walkthrough
2. Read [WORKFLOW_CUSTOMIZATION.md](./WORKFLOW_CUSTOMIZATION.md) to customize for your project
3. Review [WORKFLOW_TROUBLESHOOTING.md](./WORKFLOW_TROUBLESHOOTING.md) for common issues

---

## References

- **Agent Definitions:** `~/.claude/agent_definitions/`
- **Agent Briefings:** `.claude/agent_briefings/` (project-specific)
- **Parallel Detection:** `~/tier1_workflow_global/implementation/parallel_detection.py`
- **Assessment Document:** `~/tier1_workflow_global/docs/assessment/tier1_enhancement_assessment.md`
