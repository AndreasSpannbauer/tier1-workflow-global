# Validation System Architecture

**Week 4 Implementation**: Validation phase with retry loop and build fixer agent integration.

## Overview

The validation system (Phase 3 of the workflow) ensures code quality through automated checks with intelligent retry and auto-fix capabilities.

**Key Features:**
- **Multi-language support**: Python, TypeScript, Go, etc.
- **Retry loop**: Up to 3 attempts with automated fixing
- **Build fixer agent**: Automatically deployed on validation failures
- **Template-based**: Copy-and-customize validation scripts
- **Non-blocking**: Workflow continues even if validation ultimately fails
- **Comprehensive logging**: Track all attempts and fixes

## Architecture

### Phase 3 Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase 3: Validation                                             │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Initialize           │
                  │ - Attempt counter    │
                  │ - Max attempts = 3   │
                  │ - Logs directory     │
                  └──────────────────────┘
                             │
                             ▼
            ┌────────────────────────────────────┐
            │ Validation Retry Loop              │
            │ (while attempts < 3 && not passed) │
            └────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Run Validation       │
                  │ - npm run validate   │
                  │   OR                 │
                  │ - Fallback commands  │
                  └──────────────────────┘
                             │
                             ▼
                    ┌────────┴────────┐
                    │                 │
             ┌──────▼──────┐   ┌─────▼──────┐
             │ PASSED      │   │ FAILED     │
             │ Exit loop   │   │ Continue   │
             └─────────────┘   └────────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │ Attempts < Max?      │
                           └──────────────────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        │                           │
                 ┌──────▼──────┐            ┌──────▼──────┐
                 │ YES         │            │ NO          │
                 │ Deploy      │            │ Max reached │
                 │ Build Fixer │            │ Mark failed │
                 └─────────────┘            │ Continue    │
                        │                   └─────────────┘
                        ▼
              ┌──────────────────────┐
              │ Build Fixer Agent    │
              │ - Auto-fix lint      │
              │ - Auto-format        │
              │ - Fix type hints     │
              │ - Write results      │
              └──────────────────────┘
                        │
                        ▼
                 ┌─────────────┐
                 │ Re-validate │
                 │ (loop back) │
                 └─────────────┘
```

### Retry Loop Logic

```python
# Pseudocode
attempt = 0
max_attempts = 3
passed = False

while attempt < max_attempts and not passed:
    attempt += 1

    # Run validation
    result = run_validation()

    if result == PASSED:
        passed = True
        write_success_result()
        break
    else:
        # Validation failed
        if attempt < max_attempts:
            # Deploy build fixer
            deploy_build_fixer_agent(attempt)
            # Loop will retry validation
        else:
            # Max attempts reached
            write_failure_result()
            # Workflow continues anyway (non-blocking)
```

## Validation Types

### 1. Mandatory Validations

**Build/Compile Checks:**
- Python: `python -m py_compile` (syntax)
- TypeScript: `tsc --noEmit`
- Go: `go build ./...`

**Linting:**
- Python: `ruff check .`
- TypeScript: `eslint src/`
- Go: `golangci-lint run`

**Formatting:**
- Python: `ruff format --check .`
- TypeScript: `prettier --check src/`
- Go: `gofmt -l .`

**Type Checking:**
- Python: `mypy src/ --strict`
- TypeScript: Built into `tsc`
- Go: Built into compiler

### 2. Optional Validations

**Architecture Validation:**
- Custom script: `tools/validate_architecture.py`
- Enforces layer boundaries
- Checks import patterns
- Non-blocking failures

**Contract Validation:**
- Custom script: `tools/validate_contracts.py`
- Validates API schemas (OpenAPI, GraphQL, gRPC)
- Ensures implementation matches contracts
- Non-blocking failures

**Test Coverage:**
- Python: `pytest --cov=src --cov-report=term`
- TypeScript: `jest --coverage`
- Go: `go test -cover ./...`
- Can be made mandatory or optional

## Build Fixer Agent

### Agent Definition

**File:** `implementation/agent_definitions/build_fixer_agent_v1.md`

**Purpose:** Systematically fix validation errors through auto-fixes and manual corrections.

**Capabilities:**
1. **Auto-fix linting** - `ruff check --fix .`
2. **Auto-format** - `ruff format .`
3. **Add type hints** - Parse mypy errors and add missing types
4. **Fix import order** - Auto-fixed by ruff
5. **Fix line length** - Auto-fixed by ruff format
6. **Document blockers** - Clear reporting of unfixable issues

### Deployment

The orchestrator deploys the build fixer agent using the Task tool:

```python
# Example orchestrator code
Task(
    subagent_type="general-purpose",
    description=f"Fix validation errors for {epic_id} (attempt {attempt})",
    prompt=f"""
    YOU ARE: Build Fixer Agent V1

    [Read ~/tier1_workflow_global/implementation/agent_definitions/build_fixer_agent_v1.md]

    EPIC ID: {epic_id}

    VALIDATION LOG (failed attempt {attempt}):

    [Read .workflow/outputs/{epic_id}/validation/attempt_{attempt}.log]

    YOUR TASK: Fix ALL validation errors shown in the log above.

    Write results to: .workflow/outputs/{epic_id}/fix_attempt_{attempt}.json
    """
)
```

### Results Format

```json
{
  "status": "passed|failed",
  "attempt_number": 1,
  "epic_id": "EPIC-XXX",
  "agent_type": "build-fixer-agent-v1",
  "validation_results": {
    "lint": {
      "status": "passed",
      "command": "ruff check .",
      "errors_found": 8,
      "errors_fixed": 8,
      "auto_fixed": 7,
      "manual_fixed": 1
    },
    "format": {
      "status": "passed",
      "command": "ruff format --check .",
      "errors_found": 5,
      "errors_fixed": 5
    },
    "typecheck": {
      "status": "passed",
      "command": "mypy src/",
      "errors_found": 3,
      "errors_fixed": 3
    }
  },
  "fixes_applied": [
    {
      "file": "src/api/handlers.py",
      "issue": "Missing return type hint",
      "fix": "Added -> Response"
    },
    {
      "file": "src/models/user.py",
      "issue": "Import order violation",
      "fix": "Ran ruff check --fix (auto-fixed)"
    }
  ],
  "remaining_issues": [],
  "completion_timestamp": "2025-10-19T14:35:00Z"
}
```

## Validation Scripts

### Location

**Template Location:** `~/tier1_workflow_global/implementation/validation_scripts/`

**Project Location:** `<project>/tools/`

### Template Files

1. **validate_architecture.py** - Architecture boundary validation
2. **validate_contracts.py** - Contract/schema validation
3. **README.md** - Customization guide

### Customization

Projects **copy and customize** these templates:

```bash
# Copy templates to project
cp -r ~/tier1_workflow_global/implementation/validation_scripts/ ./tools/

# Customize for your project
# - Update layer definitions
# - Update contract file paths
# - Update validation logic
# - Add project-specific checks
```

See: `validation_scripts/README.md` for detailed customization instructions.

## Integration with package.json

Even for Python projects, use `package.json` scripts for consistency:

```json
{
  "name": "my-python-project",
  "scripts": {
    "lint:py": "ruff check .",
    "lint:py:fix": "ruff check --fix .",
    "format:py": "ruff format .",
    "format:py:check": "ruff format --check .",
    "typecheck:py": "mypy src/ --strict",
    "validate-architecture": "python3 tools/validate_architecture.py",
    "validate-contracts": "python3 tools/validate_contracts.py",
    "validate-all": "npm run lint:py && npm run format:py:check && npm run typecheck:py && npm run validate-architecture && npm run validate-contracts"
  }
}
```

**Benefits:**
- Consistent interface across projects
- Easy to document
- Easy to run from workflow
- Works for any language (Python, TypeScript, Go, etc.)

## Validation Execution

### Phase 3 Execution Path

1. **Check for validate-all script:**
   ```bash
   if package.json has "validate-all" script:
       run: npm run validate-all
   else:
       run fallback commands (ruff, mypy, tsc, etc.)
   ```

2. **Capture output:**
   ```bash
   npm run validate-all 2>&1 | tee .workflow/outputs/${EPIC_ID}/validation/attempt_${N}.log
   ```

3. **Check exit code:**
   ```bash
   if exit_code == 0:
       validation passed
   else:
       validation failed → deploy build fixer
   ```

### Fallback Commands

If `validate-all` script doesn't exist, the workflow runs default commands based on file detection:

**Python project detection:**
```bash
if [ -d "src" ] && find src -name "*.py" -type f | grep -q .; then
    # Run Python validations
fi
```

**TypeScript project detection:**
```bash
if [ -f "tsconfig.json" ]; then
    # Run TypeScript validations
fi
```

## Output Artifacts

### Validation Logs

**Location:** `.workflow/outputs/${EPIC_ID}/validation/`

**Files:**
- `attempt_1.log` - First validation attempt
- `attempt_2.log` - Second attempt (if first failed)
- `attempt_3.log` - Third attempt (if second failed)
- `result.json` - Final validation result

**result.json format:**
```json
{
  "status": "passed|failed",
  "attempts": 2,
  "final_attempt_log": ".workflow/outputs/EPIC-XXX/validation/attempt_2.log",
  "timestamp": "2025-10-19T14:35:00Z"
}
```

### Fix Attempt Logs

**Location:** `.workflow/outputs/${EPIC_ID}/`

**Files:**
- `fix_attempt_1.json` - Build fixer results (attempt 1)
- `fix_attempt_2.json` - Build fixer results (attempt 2)
- `fix_attempt_3.json` - Build fixer results (attempt 3)

## Non-Blocking Philosophy

**Key Principle:** Validation failures are **non-blocking** - the workflow continues.

**Why?**
1. **Early-stage projects** - May not have all validations configured yet
2. **Intentional skips** - Projects may choose to skip certain checks
3. **False positives** - Validation tools may report issues that aren't real problems
4. **Manual intervention** - Allows human to review and decide next steps

**What happens on failure:**
1. Validation attempted 3 times with build fixer
2. If still failing → Workflow continues to Phase 5 (Commit)
3. Warning message suggests manual review
4. GitHub issue updated with validation failure status

**To make blocking:**
```bash
# In execute-workflow.md, change:
if [ $VALIDATION_PASSED -eq 0 ]; then
    exit 1  # Block workflow
fi
```

## GitHub Integration

### Validation Status Updates

**On success:**
```bash
gh issue edit ${EPIC_ID} --add-label "status:validated"
gh issue comment ${EPIC_ID} --body "✅ Validation passed (attempt N)"
```

**On failure:**
```bash
gh issue comment ${EPIC_ID} --body "⚠️ Validation failed after N attempts"
```

## Common Validation Patterns

### Python Project

**Mandatory:**
- Linting: `ruff check .`
- Formatting: `ruff format --check .`
- Type checking: `mypy src/ --strict`

**Optional:**
- Architecture: `python3 tools/validate_architecture.py`
- Test coverage: `pytest --cov=src --cov-report=term-missing --cov-fail-under=80`

### TypeScript Project

**Mandatory:**
- Build: `tsc --noEmit`
- Linting: `eslint src/`
- Formatting: `prettier --check src/`

**Optional:**
- Architecture: `ts-node tools/validate_architecture.ts`
- Test coverage: `jest --coverage --coverageThreshold='{"global":{"lines":80}}'`

### Polyglot Project (Python + TypeScript)

**Mandatory:**
- Python: `npm run lint:py && npm run typecheck:py`
- TypeScript: `npm run build:ts && npm run lint:ts`

**Optional:**
- Architecture (both): `npm run validate-architecture`
- Contracts: `npm run validate-contracts`

## Error Messages

### Validation Passed

```
✅ Validation passed on attempt 1

────────────────────────────────────────────────────────────────────
✅ Phase 3 Complete: Validation Passed
────────────────────────────────────────────────────────────────────
   Attempts: 1
   Status: PASSED
```

### Validation Failed (Retrying)

```
❌ Validation failed on attempt 1

🔧 Deploying build fixer agent (attempt 1)...
────────────────────────────────────────────────────────────────────

Build fixer agent will:
1. Read error output
2. Apply auto-fixes (ruff check --fix, ruff format)
3. Fix manual errors
4. Write results

Retrying validation...
```

### Validation Failed (Max Attempts)

```
❌ Validation failed on attempt 3

⚠️  Maximum validation attempts (3) reached

Validation failed after 3 attempts.
Logs: .workflow/outputs/EPIC-XXX/validation/

Manual intervention recommended but workflow will continue.

────────────────────────────────────────────────────────────────────
⚠️  Phase 3 Complete: Validation Failed
────────────────────────────────────────────────────────────────────
   Attempts: 3
   Status: FAILED (workflow continues)

   Review validation logs:
   .workflow/outputs/EPIC-XXX/validation/
```

## Summary

**What you get:**
- ✅ Automated validation with retry loop
- ✅ Build fixer agent auto-deployment
- ✅ Template validation scripts (copy-and-customize)
- ✅ Multi-language support (Python, TypeScript, etc.)
- ✅ Non-blocking failures (workflow continues)
- ✅ Comprehensive logging and tracking

**What you need to do:**
1. Copy validation script templates to your project
2. Customize for your stack and architecture
3. Add `validate-all` script to package.json
4. Test validation commands
5. Run workflow (validation happens in Phase 3)

**Next Steps:**
- See: `VALIDATION_RETRY_WORKFLOW.md` for retry loop details
- See: `validation_scripts/README.md` for customization guide
- See: `test_cases/validation_*.md` for test examples
