# Tier 1 Workflow - Quick Start Guide

**Get started with the Tier 1 workflow in 5 minutes**

---

## What is This?

The Tier 1 workflow is an automated epic implementation system that uses AI agents to execute software development tasks from specification to commit.

**Benefits:**
- 2-4x faster implementation for large epics (parallel execution)
- Automated validation with retry loop
- Consistent code quality through agent briefings
- Knowledge capture via post-mortem analysis

---

## Prerequisites

- Claude Code installed and configured
- Git repository with clean working directory
- Python 3.8+ (for parallel detection and worktree management)
- Node.js (for validation scripts, if using TypeScript)

**Optional:**
- GitHub CLI (`gh`) for issue tracking
- `ruff` (Python linting) or `eslint` (TypeScript linting)
- `mypy` (Python type checking) or `tsc` (TypeScript type checking)

---

## Installation (One Command)

```bash
# Clone or copy the Tier 1 workflow template to your project
cp -r ~/tier1_workflow_global/template/.claude ~/your-project/
cp -r ~/tier1_workflow_global/template/.tasks ~/your-project/
cp -r ~/tier1_workflow_global/template/tools ~/your-project/

# Initialize directories
cd ~/your-project
mkdir -p .workflow/{outputs,post-mortem}
mkdir -p .worktrees/.metadata
```

**Verify installation:**
```bash
ls -la .claude/commands/execute-workflow.md
ls -la .tasks/
```

You should see:
- `.claude/commands/execute-workflow.md` - Workflow orchestrator
- `.tasks/backlog/` - Where epics live before execution
- `.tasks/completed/` - Where epics go after execution

---

## Your First Epic (5-Minute Example)

### Step 1: Create Epic Specification (1 minute)

```bash
# In Claude Code
/spec-epic
```

**Claude prompts:** "What feature would you like to specify?"

**You provide:**
```
Add input validation to the user registration form.

Requirements:
- Validate email format (RFC 5322 compliant)
- Validate password strength (8+ chars, 1 uppercase, 1 number)
- Display clear error messages for invalid inputs
- Integration with existing registration endpoint
```

**Claude creates:**
- `.tasks/backlog/EPIC-001-add-input-validation/spec.md`

**Example output:**
```
✅ Epic created: EPIC-001

Location: .tasks/backlog/EPIC-001-add-input-validation/spec.md

Summary:
- Title: Add input validation to user registration
- Requirements: 4 items
- Acceptance criteria: 3 items
- Technical considerations: Noted

Next steps:
1. Review spec.md
2. Run /refine-epic EPIC-001 to generate implementation plan
```

---

### Step 2: Generate Implementation Plan (1 minute)

```bash
# In Claude Code
/refine-epic EPIC-001
```

**Claude creates:**
1. `architecture.md` - Design decisions and component structure
2. `implementation-details/file-tasks.md` - Prescriptive implementation plan

**Example output:**
```
✅ Epic refined: EPIC-001

Files created:
- architecture.md (design decisions)
- implementation-details/file-tasks.md (prescriptive plan)

Files to create: 2
Files to modify: 3

Ready for execution: /execute-workflow EPIC-001
```

---

### Step 3: Execute Workflow (Auto Validation + Retry) (3 minutes)

```bash
# In Claude Code
/execute-workflow EPIC-001
```

**Claude executes all phases automatically:**

**Phase 0: Preflight**
```
🔍 Analyzing for parallel execution opportunities...

Parallel Analysis:
  Files: 5
  Domains: 1 (backend only)
  Viable: false
  Reason: Too few domains (1 < 2)

➡️ Sequential execution (parallel not viable)

✅ Preflight checks passed
```

**Phase 1A: Implementation**
```
🚀 Phase 1A: Sequential Implementation

Deploying implementation agent...
Reading prescriptive plan...

Creating src/validators/email_validator.py... ✅
Creating src/validators/password_validator.py... ✅
Modifying src/api/auth_routes.py... ✅

✅ Phase 1A Complete: Sequential Implementation
Files created: 2
Files modified: 3
```

**Phase 3: Validation with Retry Loop**
```
🔍 Phase 3: Validation

Validation Attempt 1 of 3
────────────────────────────────────────────────────────────────────

Running: npm run validate-all

❌ Validation failed on attempt 1

🔧 Deploying build fixer agent (attempt 1)...

Build fixer agent will:
1. Read error output
2. Apply auto-fixes (ruff check --fix, ruff format)
3. Fix manual errors
4. Write results

Retrying validation...

Validation Attempt 2 of 3
────────────────────────────────────────────────────────────────────

Running: npm run validate-all

✅ Validation passed on attempt 2

====================================================================
✅ Phase 3 Complete: Validation Passed
====================================================================
   Attempts: 2
   Status: PASSED
```

**Phase 5: Commit & Cleanup**
```
📝 Phase 5: Commit & Cleanup

Commit message:
──────────────────────────────────────────────────────────────────
feat(EPIC-001): Add input validation to user registration

Implementation completed using sequential execution mode.

Files created: 2
Files modified: 3
Execution mode: sequential

Epic: .tasks/backlog/EPIC-001-add-input-validation
Results: .workflow/outputs/EPIC-001/

🤖 Generated with Claude Code
https://claude.com/claude-code

Co-Authored-By: Claude <noreply@anthropic.com>
──────────────────────────────────────────────────────────────────

✅ Commit created successfully

✅ Epic moved to: .tasks/completed/EPIC-001-add-input-validation
```

**Phase 6: Post-Mortem**
```
📊 Phase 6: Post-Mortem Analysis

Analyzing workflow execution to identify improvements...

✅ Post-Mortem Report: .workflow/post-mortem/EPIC-001.md

Key Recommendations:
- Add email regex pattern to backend briefing
- Clarify error handling patterns for validation errors
- Document password strength requirements pattern
```

---

### Step 4: Review Results (30 seconds)

```bash
# View commit
git show

# View post-mortem recommendations
cat .workflow/post-mortem/EPIC-001.md

# Check epic moved to completed
ls .tasks/completed/
```

---

## That's It!

You just:
1. Created an epic specification (1 min)
2. Generated an implementation plan (1 min)
3. Executed the workflow with automated validation and retry (3 min)
4. Got a commit, validation report, and post-mortem analysis

**Total time:** 5 minutes

---

## What Happens Under the Hood?

### Sequential Execution (Small Epics)

**Triggers when:**
- File count < 8, OR
- Domain count < 2

**Flow:**
```
Spec → Architecture → Plan → Agent → Validation → Commit → Post-Mortem
```

**Performance:** ~15-30 minutes for typical epic

---

### Parallel Execution (Large Epics)

**Triggers when:**
- File count ≥ 8, AND
- Domain count ≥ 2, AND
- File overlap < 30%

**Flow:**
```
Spec → Architecture → Plan
  ↓
Parallel Detection
  ↓
Create Worktrees (backend, frontend, database)
  ↓
Deploy Agents (parallel)
  ├─► Backend Agent (worktree1)
  ├─► Frontend Agent (worktree2)
  └─► Database Agent (worktree3)
  ↓
Sequential Merge (dependency order)
  ↓
Validation → Commit → Post-Mortem
```

**Performance:** 2-4x faster than sequential (20-40 min vs 60-120 min)

**Speedup Example:**
```
Epic: 18 files, 3 domains (backend, frontend, database)
Sequential: 75 minutes
Parallel: 25 minutes
Speedup: 3x
```

---

## Common Commands

### Epic Management

```bash
# Create epic specification
/spec-epic

# Refine epic (generate implementation plan)
/refine-epic EPIC-XXX

# Execute workflow (sequential or parallel)
/execute-workflow EPIC-XXX

# List all epics
/task-list
```

### Validation

```bash
# Run validation manually
npm run validate-all

# OR for Python projects:
ruff check .
ruff format --check .
mypy src/

# OR for TypeScript projects:
npm run build
npm run lint
```

### Review Results

```bash
# View implementation results
cat .workflow/outputs/EPIC-XXX/phase1_results.json

# View validation results
cat .workflow/outputs/EPIC-XXX/validation/result.json

# View post-mortem
cat .workflow/post-mortem/EPIC-XXX.md

# View commit
git show
```

---

## Parallel Execution Example

### When Does Parallel Execution Trigger?

**Example epic with 18 files across 3 domains:**

```markdown
# file-tasks.md

## Files to Create

### Backend
- src/backend/services/email_service.py
- src/backend/api/email_routes.py
- src/backend/models/email.py
- src/backend/schemas/email.py

### Frontend
- src/frontend/components/EmailList.tsx
- src/frontend/components/EmailDetail.tsx
- src/frontend/api/emailClient.ts
- src/frontend/hooks/useEmail.ts

### Database
- migrations/001_create_emails_table.sql
- migrations/002_add_email_indexes.sql

## Files to Modify

### Backend
- src/backend/database.py
- src/backend/config.py

### Frontend
- src/frontend/App.tsx
- src/frontend/routes.tsx

### Database
- src/backend/models/__init__.py
```

**Parallel detection result:**
```json
{
  "viable": true,
  "reason": "8+ files, 2+ domains, <30% overlap",
  "file_count": 18,
  "domain_count": 3,
  "domains": {
    "backend": 6,
    "frontend": 6,
    "database": 3
  },
  "execution_mode": "parallel"
}
```

**What happens:**
```
1. Creates 3 worktrees:
   - .worktrees/EPIC-XXX-backend-a3f2b1c4/
   - .worktrees/EPIC-XXX-frontend-d5e6f7g8/
   - .worktrees/EPIC-XXX-database-h9i0j1k2/

2. Deploys 3 agents in parallel (single message):
   - Backend Agent → worktree1
   - Frontend Agent → worktree2
   - Database Agent → worktree3

3. Agents work in isolation (no conflicts)

4. Sequential merge (dependency order):
   - database → backend → frontend

5. Worktree cleanup

6. Validation → Commit → Post-Mortem
```

---

## Customization

### Add Validation Scripts

```bash
# Create validation scripts
cp ~/tier1_workflow_global/implementation/validation_scripts/* ./tools/

# Customize for your project
nano tools/validate_architecture.py
nano tools/validate_contracts.py

# Add to package.json
nano package.json
```

**Example package.json:**
```json
{
  "scripts": {
    "lint:py": "ruff check .",
    "typecheck:py": "mypy src/ --strict",
    "validate-architecture": "python3 tools/validate_architecture.py",
    "validate-all": "npm run lint:py && npm run typecheck:py && npm run validate-architecture"
  }
}
```

---

### Customize Agent Briefings

```bash
# Edit domain briefings
nano .claude/agent_briefings/backend_implementation.md
nano .claude/agent_briefings/frontend_implementation.md

# Edit project architecture
nano .claude/agent_briefings/project_architecture.md
```

**Example backend briefing addition:**
```markdown
## Error Handling Pattern

All service methods should raise custom exceptions:

```python
class EmailNotFoundError(Exception):
    pass

class EmailService:
    async def get_email(self, id: int) -> Email:
        email = await self.db.query(Email).filter(Email.id == id).first()
        if not email:
            raise EmailNotFoundError(f"Email {id} not found")
        return email
```

API routes catch and convert to HTTPException:

```python
@router.get("/emails/{id}")
async def get_email(id: int):
    try:
        return await service.get_email(id)
    except EmailNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```
```

---

## Troubleshooting

### Epic Not Ready

**Error:**
```
❌ Epic not ready for execution

Missing files:
- architecture.md
- implementation-details/file-tasks.md

Run: /refine-epic EPIC-XXX
```

**Fix:** Run `/refine-epic EPIC-XXX` to generate missing files

---

### Git Not Clean

**Error:**
```
❌ Git working directory not clean

Uncommitted changes detected
```

**Fix:**
```bash
# Option 1: Commit changes
git add .
git commit -m "WIP"

# Option 2: Stash changes
git stash

# Then re-run workflow
/execute-workflow EPIC-XXX
```

---

### Validation Fails

**What happens:**
```
❌ Validation failed on attempt 1

🔧 Deploying build fixer agent (attempt 1)...
```

Build fixer agent automatically:
1. Reads error output
2. Applies auto-fixes (`ruff check --fix`, `ruff format`)
3. Fixes manual errors (type hints, imports)
4. Retries validation

**Maximum 3 attempts** before workflow continues with warning.

---

### Parallel Execution Not Triggering

**Threshold check:**
- ✅ File count ≥ 8?
- ✅ Domain count ≥ 2?
- ✅ File overlap < 30%?

If NO to any, workflow uses sequential execution (faster for small epics).

**Force sequential:**
- Not currently supported
- Parallel detection is automatic based on thresholds

---

## Next Steps

### For Beginners

1. Try the 5-minute example above
2. Review the generated commit and post-mortem
3. Read the [User Manual](./WORKFLOW_USER_MANUAL.md) for detailed workflows
4. Customize agent briefings based on your project patterns

### For Advanced Users

1. Read the [Comprehensive Guide](./WORKFLOW_COMPREHENSIVE_GUIDE.md) for architecture details
2. Customize validation scripts in `tools/`
3. Set up GitHub integration (`gh auth login`)
4. Review post-mortem recommendations and update briefings

### For Contributors

1. Read architecture documentation in `implementation/`
2. Review agent definitions in `implementation/agent_definitions/`
3. Test with mock epics in `implementation/test_epics/`
4. See [WEEK4_DELIVERABLES.md](./WEEK4_DELIVERABLES.md) for current status

---

## Quick Reference

### Commands
```bash
/spec-epic                # Create epic specification
/refine-epic EPIC-XXX     # Generate implementation plan
/execute-workflow EPIC-XXX # Execute workflow
/task-list                # List all epics
```

### Validation
```bash
npm run validate-all      # Run all validation checks
ruff check .              # Python linting
mypy src/                 # Python type checking
```

### Results
```bash
# Implementation results
cat .workflow/outputs/EPIC-XXX/phase1_results.json

# Validation results
cat .workflow/outputs/EPIC-XXX/validation/result.json

# Post-mortem
cat .workflow/post-mortem/EPIC-XXX.md

# Commit
git show
```

### File Structure
```
your-project/
├── .claude/
│   ├── commands/
│   │   ├── execute-workflow.md     # Workflow orchestrator
│   │   ├── spec-epic.md            # Create epic
│   │   └── refine-epic.md          # Generate plan
│   └── agent_briefings/
│       ├── backend_implementation.md
│       ├── frontend_implementation.md
│       └── project_architecture.md
├── .tasks/
│   ├── backlog/                    # Epics before execution
│   └── completed/                  # Epics after execution
├── .workflow/
│   ├── outputs/                    # Implementation results
│   └── post-mortem/                # Post-mortem reports
└── tools/
    ├── validate_architecture.py    # Architecture validation
    └── validate_contracts.py       # Contract validation
```

---

## Support

**Documentation:**
- [User Manual](./WORKFLOW_USER_MANUAL.md) - Detailed user guide
- [Comprehensive Guide](./WORKFLOW_COMPREHENSIVE_GUIDE.md) - Technical deep dive
- [Week 4 Deliverables](./WEEK4_DELIVERABLES.md) - Current status

**Issues:**
- Review troubleshooting section above
- Check [WORKFLOW_TROUBLESHOOTING.md](./WORKFLOW_TROUBLESHOOTING.md)
- See [WORKFLOW_TESTING_GUIDE.md](./WORKFLOW_TESTING_GUIDE.md) for test scenarios

---

**Generated:** 2025-10-19
**Version:** 1.0
**Status:** Production Ready
