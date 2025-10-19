# Validation Retry Workflow - Deep Dive

**Week 4 Implementation**: Detailed explanation of the validation retry loop with build fixer agent integration.

## Overview

The validation retry loop automatically attempts to fix validation errors up to 3 times using the build fixer agent.

**Flow:** Validate → Fail → Deploy Fixer → Re-Validate → Repeat (max 3x)

## Retry Loop State Machine

```
State: INIT
├─ attempt = 0
├─ max_attempts = 3
└─ passed = False

State: VALIDATING (attempt N)
├─ Run validation commands
├─ Capture output to log
└─ Check exit code
    ├─ Exit code = 0 → State: PASSED
    └─ Exit code ≠ 0 → State: FAILED

State: FAILED (attempt N)
├─ Check: attempt < max_attempts?
│   ├─ YES → State: FIXING
│   └─ NO → State: MAX_REACHED
└─ Log failure

State: FIXING (attempt N)
├─ Read validation log
├─ Deploy build fixer agent (Task tool)
├─ Wait for agent completion
├─ Read fix results
└─ State: VALIDATING (attempt N+1)

State: MAX_REACHED
├─ Write failure result
├─ Log max attempts reached
└─ State: CONTINUE (non-blocking)

State: PASSED
├─ Write success result
├─ Exit retry loop
└─ Proceed to Phase 5

State: CONTINUE
├─ Workflow continues despite failure
└─ Proceed to Phase 5
```

## Detailed Workflow

### Initialization

```bash
# Phase 3 starts
echo "🔍 Phase 3: Validation"

# Initialize state
VALIDATION_ATTEMPT=0
MAX_VALIDATION_ATTEMPTS=3
VALIDATION_PASSED=0

# Create logs directory
mkdir -p .workflow/outputs/${EPIC_ID}/validation
```

**State variables:**
- `VALIDATION_ATTEMPT` - Current attempt number (0-3)
- `MAX_VALIDATION_ATTEMPTS` - Maximum retries (3)
- `VALIDATION_PASSED` - Boolean flag (0 = not passed, 1 = passed)

### Loop Entry Condition

```bash
while [ $VALIDATION_ATTEMPT -lt $MAX_VALIDATION_ATTEMPTS ] && [ $VALIDATION_PASSED -eq 0 ]; do
    # Loop body
done
```

**Loop continues while:**
- `attempt < 3` AND
- `not passed`

**Loop exits when:**
- `attempt >= 3` OR
- `passed == true`

### Attempt N: Validation Execution

```bash
VALIDATION_ATTEMPT=$((VALIDATION_ATTEMPT + 1))

echo "────────────────────────────────────────────────────────────────────"
echo "Validation Attempt $VALIDATION_ATTEMPT of $MAX_VALIDATION_ATTEMPTS"
echo "────────────────────────────────────────────────────────────────────"

# Run validation
VALIDATION_EXIT_CODE=0

if package.json has "validate-all" script:
    npm run validate-all 2>&1 | tee .workflow/outputs/${EPIC_ID}/validation/attempt_${VALIDATION_ATTEMPT}.log
    VALIDATION_EXIT_CODE=${PIPESTATUS[0]}
else:
    # Run fallback commands
    # ... (see VALIDATION_SYSTEM.md)
fi
```

**Key points:**
1. Increment attempt counter
2. Run validation commands
3. Capture stdout/stderr to log file
4. Save exit code

### Decision Point: Pass or Fail?

```bash
if [ $VALIDATION_EXIT_CODE -eq 0 ]; then
    # PASSED - exit loop
    echo "✅ Validation passed on attempt $VALIDATION_ATTEMPT"
    VALIDATION_PASSED=1

    # Write success result
    cat > .workflow/outputs/${EPIC_ID}/validation/result.json << EOF
{
  "status": "passed",
  "attempts": $VALIDATION_ATTEMPT,
  "final_attempt_log": ".workflow/outputs/${EPIC_ID}/validation/attempt_${VALIDATION_ATTEMPT}.log",
  "timestamp": "$(date -Iseconds)"
}
EOF

else
    # FAILED - check if we should retry
    echo "❌ Validation failed on attempt $VALIDATION_ATTEMPT"

    if [ $VALIDATION_ATTEMPT -lt $MAX_VALIDATION_ATTEMPTS ]; then
        # Deploy build fixer and retry
    else
        # Max attempts reached
    fi
fi
```

**Pass path:**
1. Set `VALIDATION_PASSED=1`
2. Write success result
3. Loop exits (condition no longer met)

**Fail path:**
1. Check if more attempts available
2. If yes → Deploy fixer and retry
3. If no → Write failure result and exit

### Build Fixer Deployment

```bash
if [ $VALIDATION_ATTEMPT -lt $MAX_VALIDATION_ATTEMPTS ]; then
    echo "🔧 Deploying build fixer agent (attempt $VALIDATION_ATTEMPT)..."

    # Build fixer agent prompt
    FIXER_PROMPT=$(cat << 'FIXER_EOF'
YOU ARE: Build Fixer Agent V1

[Read ~/tier1_workflow_global/implementation/agent_definitions/build_fixer_agent_v1.md]

EPIC ID: ${EPIC_ID}

VALIDATION LOG (failed attempt ${VALIDATION_ATTEMPT}):

[Read .workflow/outputs/${EPIC_ID}/validation/attempt_${VALIDATION_ATTEMPT}.log]

YOUR TASK: Fix ALL validation errors shown in the log above.

Write results to: .workflow/outputs/${EPIC_ID}/fix_attempt_${VALIDATION_ATTEMPT}.json
FIXER_EOF
)

    # Orchestrator deploys agent here using Task tool
    # Task(subagent_type="general-purpose", description="Fix validation errors", prompt=FIXER_PROMPT)

    # Wait for agent to complete

    # Read fix results
    FIX_RESULT_FILE=".workflow/outputs/${EPIC_ID}/fix_attempt_${VALIDATION_ATTEMPT}.json"

    if [ -f "$FIX_RESULT_FILE" ]; then
        FIX_STATUS=$(jq -r '.status' "$FIX_RESULT_FILE")
        echo "Build fixer result: $FIX_STATUS"

        if [ "$FIX_STATUS" = "passed" ]; then
            echo "  ✅ Build fixer successfully fixed all issues"
        else
            echo "  ⚠️  Build fixer could not fix all issues"
            jq -r '.remaining_issues[]? | "    - \(.issue)"' "$FIX_RESULT_FILE"
        fi
    fi

    echo "Retrying validation..."
    # Loop continues → Re-validate
fi
```

**Orchestrator's role:**
1. Construct fixer agent prompt
2. Deploy agent using Task tool
3. Wait for agent completion
4. Read fix results
5. Continue loop (re-validate)

**Agent's role:**
1. Read validation log
2. Apply auto-fixes (`ruff check --fix`, `ruff format`)
3. Fix manual errors (type hints, imports)
4. Re-run validation
5. Write structured results

### Max Attempts Reached

```bash
else:  # attempt >= max_attempts
    echo "⚠️  Maximum validation attempts ($MAX_VALIDATION_ATTEMPTS) reached"
    echo "Validation failed after $VALIDATION_ATTEMPT attempts."
    echo "Manual intervention recommended but workflow will continue."

    # Write failure result
    cat > .workflow/outputs/${EPIC_ID}/validation/result.json << EOF
{
  "status": "failed",
  "attempts": $VALIDATION_ATTEMPT,
  "final_attempt_log": ".workflow/outputs/${EPIC_ID}/validation/attempt_${VALIDATION_ATTEMPT}.log",
  "max_attempts_reached": true,
  "timestamp": "$(date -Iseconds)"
}
EOF

    # Loop exits (condition no longer met)
    # Workflow continues to Phase 5
fi
```

**Key points:**
1. Loop cannot continue (max attempts)
2. Write failure result with `max_attempts_reached: true`
3. Workflow continues anyway (non-blocking)
4. Manual intervention suggested

## Example Execution Traces

### Trace 1: Pass on First Attempt

```
🔍 Phase 3: Validation
====================================================================

────────────────────────────────────────────────────────────────────
Validation Attempt 1 of 3
────────────────────────────────────────────────────────────────────

Running: npm run validate-all

> my-project@1.0.0 validate-all
> npm run lint:py && npm run typecheck:py

✓ ruff check . passed
✓ mypy src/ passed

✅ Validation passed on attempt 1

====================================================================
✅ Phase 3 Complete: Validation Passed
====================================================================
   Attempts: 1
   Status: PASSED
```

**Result:** 1 attempt, immediate success.

### Trace 2: Fail → Fix → Pass

```
🔍 Phase 3: Validation
====================================================================

────────────────────────────────────────────────────────────────────
Validation Attempt 1 of 3
────────────────────────────────────────────────────────────────────

Running: npm run validate-all

> my-project@1.0.0 validate-all
> npm run lint:py && npm run typecheck:py

✗ ruff check . failed
  src/api/handlers.py:15:5 F401 'os' imported but unused
  src/models/user.py:8:1 I001 Import block is un-sorted

✗ mypy src/ failed
  src/api/handlers.py:20: error: Function is missing a return type annotation

❌ Validation failed on attempt 1

🔧 Deploying build fixer agent (attempt 1)...
────────────────────────────────────────────────────────────────────

[Agent executes:]
- Ran: ruff check --fix . (fixed 2 issues)
- Added type hint: def get_user() -> User:
- Re-ran validation: ALL PASSED

Build fixer result: passed
  ✅ Build fixer successfully fixed all issues

Retrying validation...

────────────────────────────────────────────────────────────────────
Validation Attempt 2 of 3
────────────────────────────────────────────────────────────────────

Running: npm run validate-all

✓ ruff check . passed
✓ mypy src/ passed

✅ Validation passed on attempt 2

====================================================================
✅ Phase 3 Complete: Validation Passed
====================================================================
   Attempts: 2
   Status: PASSED
```

**Result:** 2 attempts, fixed by agent, success.

### Trace 3: Max Attempts Reached

```
🔍 Phase 3: Validation
====================================================================

────────────────────────────────────────────────────────────────────
Validation Attempt 1 of 3
────────────────────────────────────────────────────────────────────

Running: npm run validate-all

✗ mypy src/ failed
  src/complex/module.py:50: error: Incompatible return type

❌ Validation failed on attempt 1

🔧 Deploying build fixer agent (attempt 1)...

Build fixer result: failed
  ⚠️  Build fixer could not fix all issues
    - mypy: Incompatible return type (needs spec clarification)

Retrying validation...

────────────────────────────────────────────────────────────────────
Validation Attempt 2 of 3
────────────────────────────────────────────────────────────────────

✗ mypy src/ failed (same error)

❌ Validation failed on attempt 2

🔧 Deploying build fixer agent (attempt 2)...

Build fixer result: failed (same blocker)

Retrying validation...

────────────────────────────────────────────────────────────────────
Validation Attempt 3 of 3
────────────────────────────────────────────────────────────────────

✗ mypy src/ failed (same error)

❌ Validation failed on attempt 3

⚠️  Maximum validation attempts (3) reached

Validation failed after 3 attempts.
Logs: .workflow/outputs/EPIC-XXX/validation/

Manual intervention recommended but workflow will continue.

====================================================================
⚠️  Phase 3 Complete: Validation Failed
====================================================================
   Attempts: 3
   Status: FAILED (workflow continues)

   Review validation logs:
   .workflow/outputs/EPIC-XXX/validation/
```

**Result:** 3 attempts, all failed, workflow continues.

## File Artifacts

### After Attempt 1 (Pass)

```
.workflow/outputs/EPIC-XXX/
└── validation/
    ├── attempt_1.log          # Validation output (success)
    └── result.json            # { "status": "passed", "attempts": 1 }
```

### After Attempt 2 (Fail → Fix → Pass)

```
.workflow/outputs/EPIC-XXX/
├── fix_attempt_1.json         # Build fixer results (attempt 1)
└── validation/
    ├── attempt_1.log          # Validation output (failed)
    ├── attempt_2.log          # Validation output (success)
    └── result.json            # { "status": "passed", "attempts": 2 }
```

### After Attempt 3 (Max Reached)

```
.workflow/outputs/EPIC-XXX/
├── fix_attempt_1.json         # Build fixer results (attempt 1)
├── fix_attempt_2.json         # Build fixer results (attempt 2)
└── validation/
    ├── attempt_1.log          # Failed
    ├── attempt_2.log          # Failed
    ├── attempt_3.log          # Failed
    └── result.json            # { "status": "failed", "attempts": 3, "max_attempts_reached": true }
```

## Agent Communication Protocol

### Orchestrator → Build Fixer Agent

**Input:**
1. Agent definition: `~/tier1_workflow_global/implementation/agent_definitions/build_fixer_agent_v1.md`
2. Validation log: `.workflow/outputs/${EPIC_ID}/validation/attempt_${N}.log`
3. Epic context: `${EPIC_ID}`

**Prompt structure:**
```markdown
YOU ARE: Build Fixer Agent V1

[Agent definition]

EPIC ID: EPIC-XXX

VALIDATION LOG (failed attempt N):

[Validation log contents]

YOUR TASK: Fix ALL validation errors shown in the log above.

Write results to: .workflow/outputs/EPIC-XXX/fix_attempt_N.json
```

### Build Fixer Agent → Orchestrator

**Output:**
- Results file: `.workflow/outputs/${EPIC_ID}/fix_attempt_${N}.json`

**Results structure:**
```json
{
  "status": "passed|failed",
  "attempt_number": 1,
  "epic_id": "EPIC-XXX",
  "agent_type": "build-fixer-agent-v1",
  "validation_results": {
    "lint": { "status": "passed", "errors_fixed": 5 },
    "format": { "status": "passed", "errors_fixed": 3 },
    "typecheck": { "status": "failed", "remaining_errors": 1 }
  },
  "fixes_applied": [
    { "file": "src/api.py", "issue": "Unused import", "fix": "Auto-fixed by ruff" }
  ],
  "remaining_issues": [
    { "file": "src/api.py", "issue": "Type incompatibility", "blocker_reason": "Needs spec clarification" }
  ],
  "completion_timestamp": "2025-10-19T14:35:00Z"
}
```

### Orchestrator Processing

```bash
# Read fix results
FIX_STATUS=$(jq -r '.status' fix_attempt_N.json)

if [ "$FIX_STATUS" = "passed" ]; then
    # All issues fixed → re-validate
    echo "✅ Build fixer fixed all issues"
else
    # Some issues remain → re-validate anyway (might reduce errors)
    echo "⚠️ Build fixer could not fix all issues"
    jq -r '.remaining_issues[] | "  - \(.issue)"' fix_attempt_N.json
fi

# Continue loop → Re-validate
```

## Common Patterns

### Pattern 1: Auto-Fixable Errors Only

**Errors:**
- Import order violations
- Formatting issues
- Unused imports

**Fix:**
```bash
ruff check --fix .
ruff format .
```

**Result:** Fixed in 1 attempt.

### Pattern 2: Mixed Auto-Fix + Manual

**Errors:**
- Import order violations (auto-fix)
- Missing type hints (manual)

**Fix:**
```bash
ruff check --fix .
# Agent adds: def get_user(id: int) -> User:
```

**Result:** Fixed in 1 attempt.

### Pattern 3: Unfixable (Needs Spec Clarification)

**Errors:**
- Incompatible return type
- Missing data structure
- Unclear requirements

**Fix:**
```python
# Agent cannot fix without spec clarification
# remaining_issues: [{"blocker_reason": "Needs spec clarification"}]
```

**Result:** Failed after 3 attempts → Manual intervention.

## Best Practices

### 1. Configure Auto-Fixes First

Enable auto-fix tools in project config:

```toml
# pyproject.toml
[tool.ruff]
fix = true
unsafe-fixes = false
```

This maximizes what the build fixer can fix automatically.

### 2. Clear Error Messages

Ensure validation tools produce actionable errors:

```bash
# Good: File and line number
src/api.py:15:5: error: Missing type hint

# Bad: Generic message
Type checking failed
```

### 3. Incremental Validation

Run faster checks first:

```json
{
  "scripts": {
    "validate-all": "npm run lint:py && npm run format:py:check && npm run typecheck:py"
  }
}
```

Linting is fastest → catch easy errors early.

### 4. Document Blockers

If build fixer can't fix something, document why:

```json
{
  "remaining_issues": [
    {
      "file": "src/api.py",
      "issue": "Incompatible return type: expected User, got Optional[User]",
      "blocker_reason": "Spec doesn't specify if None is allowed. Need clarification."
    }
  ]
}
```

This helps humans fix it after max attempts.

### 5. Monitor Retry Patterns

Track which validations frequently fail:

```bash
# Analyze logs
grep "Validation failed" .workflow/outputs/*/validation/result.json

# Common failure points → improve validation scripts or agent
```

## Troubleshooting

### Issue: Agent Doesn't Fix Anything

**Symptoms:**
- Fix results show `status: "failed"`
- All errors remain

**Causes:**
- Agent can't parse error messages
- Errors require manual intervention
- Validation commands not found

**Solutions:**
1. Check error message format is parseable
2. Add auto-fix tools (ruff, prettier)
3. Update build fixer agent definition

### Issue: Loop Never Exits

**Symptoms:**
- Validation runs more than 3 times
- Loop stuck

**Causes:**
- Loop condition bug
- VALIDATION_PASSED not being set

**Solutions:**
1. Check loop condition logic
2. Verify VALIDATION_PASSED=1 is set on success
3. Add debug logging

### Issue: Validation Passes but Code is Broken

**Symptoms:**
- Validation succeeds
- Tests fail or code doesn't work

**Causes:**
- Validation too lenient
- Missing validation checks

**Solutions:**
1. Add stricter validation rules
2. Include test execution in validation
3. Add architecture/contract validation

## Summary

**Retry loop benefits:**
- ✅ Automatically fixes common errors
- ✅ Reduces manual intervention
- ✅ Up to 3 attempts before giving up
- ✅ Non-blocking failures
- ✅ Comprehensive logging

**How it works:**
1. Run validation
2. If fails → Deploy build fixer agent
3. Agent fixes errors
4. Re-run validation
5. Repeat up to 3 times
6. Continue workflow regardless

**Key files:**
- Loop logic: `template/.claude/commands/execute-workflow.md` (Phase 3)
- Agent definition: `implementation/agent_definitions/build_fixer_agent_v1.md`
- Validation logs: `.workflow/outputs/${EPIC_ID}/validation/`
- Fix results: `.workflow/outputs/${EPIC_ID}/fix_attempt_N.json`

**Next steps:**
- See: `VALIDATION_SYSTEM.md` for architecture overview
- See: `validation_scripts/README.md` for customization
- See: `test_cases/validation_*.md` for test examples
