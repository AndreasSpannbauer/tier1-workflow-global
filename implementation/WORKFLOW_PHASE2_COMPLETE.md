---
phase: validation-with-retry-loop
description: Phase 2 content for execute-workflow.md with Python validation and automatic fixing
created: 2025-10-19
validates:
  - Python linting (Ruff)
  - Python formatting (Ruff)
  - Python type checking (mypy)
  - Architecture boundaries (optional)
  - Contract compliance (optional)
  - Existing tests (optional)
---

# Phase 2: Validation with Retry Loop

## Overview

Phase 2 implements comprehensive Python validation with automatic retry logic. If validation fails, a Build Fixer Agent is deployed to fix errors systematically. The workflow blocks progression if validation fails after max attempts.

**Key Features:**
- Mandatory Python validation (lint, format, typecheck)
- Optional architecture/contract validation
- Max 3 retry attempts with fixer agent
- Structured error output and fix tracking
- Workflow blocking on persistent failures

---

## Step 1: Run Python Validation Commands

```bash
echo "🔍 Phase 2: Validation"
echo ""

VALIDATION_FAILED=0
LINT_FAILED=0
FORMAT_FAILED=0
TYPE_FAILED=0
ARCH_FAILED=0
CONTRACT_FAILED=0
TEST_FAILED=0

# Create validation output directory
VALIDATION_DIR=".workflow/outputs/${ARGUMENTS}/validation"
mkdir -p "$VALIDATION_DIR"

# ===== MANDATORY: Python Linting =====
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -d "src/" ]; then
  echo "▸ Running Python linting (Ruff)..."

  if npm run lint:py 2>&1 | tee "$VALIDATION_DIR/lint_output.log"; then
    echo "  ✅ Linting passed"
  else
    echo "  ❌ Linting failed"
    LINT_FAILED=1
    VALIDATION_FAILED=1
  fi

  echo ""
fi

# ===== MANDATORY: Python Formatting =====
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -d "src/" ]; then
  echo "▸ Running Python formatting check (Ruff)..."

  if npm run format:py:check 2>&1 | tee "$VALIDATION_DIR/format_output.log"; then
    echo "  ✅ Formatting passed"
  else
    echo "  ❌ Formatting failed"
    FORMAT_FAILED=1
    VALIDATION_FAILED=1
  fi

  echo ""
fi

# ===== MANDATORY: Type Checking (if type hints present) =====
if grep -r "from typing import\|-> \|: int\|: str" src/ 2>/dev/null | head -1 >/dev/null; then
  echo "▸ Running Python type checking (mypy)..."

  if npm run typecheck:py 2>&1 | tee "$VALIDATION_DIR/typecheck_output.log"; then
    echo "  ✅ Type checking passed"
  else
    echo "  ❌ Type checking failed"
    TYPE_FAILED=1
    VALIDATION_FAILED=1
  fi

  echo ""
fi

# ===== OPTIONAL: Architecture Validation =====
if [ -f "tools/validate_architecture.py" ]; then
  echo "▸ Running architecture validation..."

  if npm run validate-architecture 2>&1 | tee "$VALIDATION_DIR/architecture_output.log"; then
    echo "  ✅ Architecture validation passed"
  else
    echo "  ⚠️ Architecture validation failed"
    ARCH_FAILED=1
    VALIDATION_FAILED=1
  fi

  echo ""
fi

# ===== OPTIONAL: Contract Validation =====
if [ -f "tools/validate_contracts.py" ]; then
  echo "▸ Running contract validation..."

  if npm run validate-contracts 2>&1 | tee "$VALIDATION_DIR/contracts_output.log"; then
    echo "  ✅ Contract validation passed"
  else
    echo "  ⚠️ Contract validation failed"
    CONTRACT_FAILED=1
    VALIDATION_FAILED=1
  fi

  echo ""
fi

# ===== OPTIONAL: Run Existing Tests (non-blocking) =====
if [ -d "tests/" ] && [ -f "pyproject.toml" ]; then
  echo "▸ Running existing tests (optional)..."

  if npm run test:py 2>&1 | tee "$VALIDATION_DIR/test_output.log"; then
    echo "  ✅ Tests passed"
  else
    echo "  ⚠️ Tests failed (non-blocking - review required)"
    TEST_FAILED=1
    # Note: Tests do NOT block workflow
  fi

  echo ""
fi

# Store validation status
cat > "$VALIDATION_DIR/validation_status.json" << EOF
{
  "validation_passed": $([ "$VALIDATION_FAILED" -eq 0 ] && echo "true" || echo "false"),
  "checks": {
    "lint": $([ "$LINT_FAILED" -eq 0 ] && echo "\"passed\"" || echo "\"failed\""),
    "format": $([ "$FORMAT_FAILED" -eq 0 ] && echo "\"passed\"" || echo "\"failed\""),
    "typecheck": $([ "$TYPE_FAILED" -eq 0 ] && echo "\"passed\"" || echo "\"failed\""),
    "architecture": $([ "$ARCH_FAILED" -eq 0 ] && echo "\"passed\"" || echo "\"failed\""),
    "contracts": $([ "$CONTRACT_FAILED" -eq 0 ] && echo "\"passed\"" || echo "\"failed\""),
    "tests": $([ "$TEST_FAILED" -eq 0 ] && echo "\"passed\"" || echo "\"failed (non-blocking)\"")
  },
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
```

---

## Step 2: Retry Loop with Fixer Agent

```markdown
If validation fails, retry with fixer agent (max 3 attempts):
```

```bash
if [ "$VALIDATION_FAILED" -eq 1 ]; then
  echo "⚠️ Validation failed - initiating retry loop"
  echo ""

  MAX_ATTEMPTS=3
  ATTEMPT=0
  VALIDATION_PASSED=0

  while [ $VALIDATION_PASSED -eq 0 ] && [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔧 Fix Attempt $ATTEMPT/$MAX_ATTEMPTS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Collect error output
    ERROR_OUTPUT=""

    if [ "$LINT_FAILED" -eq 1 ]; then
      ERROR_OUTPUT+="=== LINT ERRORS ===\n"
      ERROR_OUTPUT+="$(cat $VALIDATION_DIR/lint_output.log | tail -50)\n\n"
    fi

    if [ "$FORMAT_FAILED" -eq 1 ]; then
      ERROR_OUTPUT+="=== FORMAT ERRORS ===\n"
      ERROR_OUTPUT+="$(cat $VALIDATION_DIR/format_output.log | tail -50)\n\n"
    fi

    if [ "$TYPE_FAILED" -eq 1 ]; then
      ERROR_OUTPUT+="=== TYPE CHECKING ERRORS ===\n"
      ERROR_OUTPUT+="$(cat $VALIDATION_DIR/typecheck_output.log | tail -50)\n\n"
    fi

    if [ "$ARCH_FAILED" -eq 1 ]; then
      ERROR_OUTPUT+="=== ARCHITECTURE ERRORS ===\n"
      ERROR_OUTPUT+="$(cat $VALIDATION_DIR/architecture_output.log | tail -50)\n\n"
    fi

    # Write error summary for agent
    echo -e "$ERROR_OUTPUT" > "$VALIDATION_DIR/errors_attempt_${ATTEMPT}.log"

    # Deploy Build Fixer Agent
    echo "Deploying Build Fixer Agent..."
    echo ""

    Task(
      subagent_type="general-purpose",
      description="Fix validation errors (attempt $ATTEMPT/$MAX_ATTEMPTS)",
      prompt=f"""
YOU ARE: Build Fixer Agent V1

{read_file(".claude/agent_definitions/build_fixer_agent_v1.md")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK: Fix ALL Python Validation Errors
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EPIC: ${ARGUMENTS}
ATTEMPT: $ATTEMPT of $MAX_ATTEMPTS

FAILED CHECKS:
$([ "$LINT_FAILED" -eq 1 ] && echo "- ❌ Linting (Ruff)")
$([ "$FORMAT_FAILED" -eq 1 ] && echo "- ❌ Formatting (Ruff)")
$([ "$TYPE_FAILED" -eq 1 ] && echo "- ❌ Type checking (mypy)")
$([ "$ARCH_FAILED" -eq 1 ] && echo "- ❌ Architecture validation")

ERROR OUTPUT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{read_file(f"$VALIDATION_DIR/errors_attempt_${ATTEMPT}.log")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSTRUCTIONS:

1. **Auto-fix what's possible:**
   ```bash
   ruff check --fix .       # Fix linting errors
   ruff format .            # Fix formatting
   ```

2. **Manually fix remaining errors:**
   - Add missing type hints
   - Fix type incompatibilities
   - Resolve import errors
   - Fix architectural boundary violations

3. **Re-run validation:**
   ```bash
   npm run validate-all
   ```

4. **Write structured results:**
   File: .workflow/outputs/${ARGUMENTS}/validation/fix_attempt_${ATTEMPT}.json

   Format (see agent definition for full schema):
   ```json
   {
     "status": "passed|failed",
     "attempt_number": $ATTEMPT,
     "epic_id": "${ARGUMENTS}",
     "validation_results": {
       "lint": {"status": "passed|failed", "errors_found": X, "errors_fixed": Y},
       "format": {"status": "passed|failed", ...},
       "typecheck": {"status": "passed|failed", ...}
     },
     "fixes_applied": [
       {"file": "...", "issue": "...", "fix": "..."}
     ],
     "remaining_issues": [
       {"file": "...", "issue": "...", "blocker_reason": "..."}
     ]
   }
   ```

CRITICAL RULES:
- DO NOT mark status as "passed" unless ALL validations pass
- DO NOT modify functionality - only fix errors
- DO NOT skip validation steps
- DO NOT exceed this attempt (you have $((MAX_ATTEMPTS - ATTEMPT)) attempts remaining)

BEGIN FIXING.
      """
    )

    # Wait for agent completion
    echo "Waiting for fixer agent to complete..."
    # (Task tool waits automatically)

    # Check if results file exists
    if [ ! -f "$VALIDATION_DIR/fix_attempt_${ATTEMPT}.json" ]; then
      echo "❌ ERROR: Fixer agent did not write results file"
      echo "Expected: $VALIDATION_DIR/fix_attempt_${ATTEMPT}.json"
      break
    fi

    # Read agent results
    FIX_STATUS=$(jq -r '.status' "$VALIDATION_DIR/fix_attempt_${ATTEMPT}.json")

    echo ""
    echo "Fixer agent completed with status: $FIX_STATUS"
    echo ""

    # Re-run validation to verify fixes
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 Re-running validation after fixes..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    VALIDATION_FAILED=0
    LINT_FAILED=0
    FORMAT_FAILED=0
    TYPE_FAILED=0
    ARCH_FAILED=0

    # Re-run all checks (same as Step 1, but shorter output)
    if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -d "src/" ]; then
      npm run lint:py >/dev/null 2>&1 || { LINT_FAILED=1; VALIDATION_FAILED=1; }
      npm run format:py:check >/dev/null 2>&1 || { FORMAT_FAILED=1; VALIDATION_FAILED=1; }
    fi

    if grep -r "from typing import\|-> \|: int\|: str" src/ 2>/dev/null | head -1 >/dev/null; then
      npm run typecheck:py >/dev/null 2>&1 || { TYPE_FAILED=1; VALIDATION_FAILED=1; }
    fi

    if [ -f "tools/validate_architecture.py" ]; then
      npm run validate-architecture >/dev/null 2>&1 || { ARCH_FAILED=1; VALIDATION_FAILED=1; }
    fi

    # Check if all passed
    if [ "$VALIDATION_FAILED" -eq 0 ]; then
      VALIDATION_PASSED=1
      echo "✅ Validation passed on attempt $ATTEMPT"
      echo ""

      # Update status file
      cat > "$VALIDATION_DIR/validation_status.json" << EOF
{
  "validation_passed": true,
  "attempts_required": $ATTEMPT,
  "checks": {
    "lint": "passed",
    "format": "passed",
    "typecheck": "passed",
    "architecture": "passed"
  },
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    else
      echo "❌ Validation still failing after attempt $ATTEMPT"
      echo ""

      # Show which checks still fail
      [ "$LINT_FAILED" -eq 1 ] && echo "  • Linting: ❌ still failing"
      [ "$FORMAT_FAILED" -eq 1 ] && echo "  • Formatting: ❌ still failing"
      [ "$TYPE_FAILED" -eq 1 ] && echo "  • Type checking: ❌ still failing"
      [ "$ARCH_FAILED" -eq 1 ] && echo "  • Architecture: ❌ still failing"
      echo ""
    fi

  done

  # Check final status after retry loop
  if [ "$VALIDATION_PASSED" -eq 0 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ WORKFLOW BLOCKED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Validation failed after $MAX_ATTEMPTS attempts."
    echo ""
    echo "Manual intervention required."
    echo ""
    echo "Review:"
    echo "  • Error logs: $VALIDATION_DIR/"
    echo "  • Fix attempts: $VALIDATION_DIR/fix_attempt_*.json"
    echo ""
    echo "Common issues:"
    echo "  • Missing dependencies (install with pip)"
    echo "  • Unclear type requirements (check spec)"
    echo "  • Architecture violations (review boundaries)"
    echo ""

    exit 1
  fi
else
  echo "✅ Validation passed on first attempt"
  echo ""
fi
```

---

## Step 3: Optional Test Execution

```bash
# ===== OPTIONAL: Run Existing Tests =====
# Note: Tests are non-blocking and informational only

if [ -d "tests/" ] && [ -f "pyproject.toml" ]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🧪 Running Existing Tests (Optional)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "Note: Tests are informational. Failures do not block workflow."
  echo ""

  if npm run test:py 2>&1 | tee "$VALIDATION_DIR/test_output.log"; then
    echo ""
    echo "✅ All tests passed"
    TEST_STATUS="passed"
  else
    echo ""
    echo "⚠️ Some tests failed"
    echo ""
    echo "Review test output: $VALIDATION_DIR/test_output.log"
    echo "Fix if necessary, but workflow continues."
    TEST_STATUS="failed"
  fi

  echo ""
else
  TEST_STATUS="skipped"
fi
```

---

## Step 4: Validation Summary

```bash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Phase 2 Complete: Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Display summary table
echo "Validation Results:"
echo ""
echo "  Linting:              $([ "$LINT_FAILED" -eq 0 ] && echo "✅ passed" || echo "❌ failed")"
echo "  Formatting:           $([ "$FORMAT_FAILED" -eq 0 ] && echo "✅ passed" || echo "❌ failed")"
echo "  Type checking:        $([ "$TYPE_FAILED" -eq 0 ] && echo "✅ passed" || echo "❌ failed")"

if [ -f "tools/validate_architecture.py" ]; then
  echo "  Architecture:         $([ "$ARCH_FAILED" -eq 0 ] && echo "✅ passed" || echo "⚠️ failed")"
fi

if [ -f "tools/validate_contracts.py" ]; then
  echo "  Contracts:            $([ "$CONTRACT_FAILED" -eq 0 ] && echo "✅ passed" || echo "⚠️ failed")"
fi

if [ -d "tests/" ]; then
  echo "  Tests:                $([ "$TEST_STATUS" = "passed" ] && echo "✅ passed" || echo "⚠️ failed (non-blocking)")"
fi

echo ""

if [ "$ATTEMPT" -gt 0 ]; then
  echo "Fix attempts: $ATTEMPT/$MAX_ATTEMPTS"
  echo ""
fi

echo "Validation artifacts:"
echo "  • Status:       $VALIDATION_DIR/validation_status.json"
echo "  • Logs:         $VALIDATION_DIR/*.log"
if [ "$ATTEMPT" -gt 0 ]; then
  echo "  • Fix results:  $VALIDATION_DIR/fix_attempt_*.json"
fi
echo ""
```

---

## Validation Script Requirements

**Ensure `package.json` has these scripts (or create them):**

```json
{
  "scripts": {
    "// ===== PYTHON LINTING =====": "",
    "lint:py": "ruff check .",
    "lint:py:fix": "ruff check --fix .",

    "// ===== PYTHON FORMATTING =====": "",
    "format:py": "ruff format .",
    "format:py:check": "ruff format --check .",

    "// ===== PYTHON TYPE CHECKING =====": "",
    "typecheck:py": "mypy src/ --strict",

    "// ===== ARCHITECTURE VALIDATION (OPTIONAL) =====": "",
    "validate-architecture": "python3 tools/validate_architecture.py",

    "// ===== CONTRACT VALIDATION (OPTIONAL) =====": "",
    "validate-contracts": "python3 tools/validate_contracts.py",

    "// ===== TESTING (OPTIONAL) =====": "",
    "test:py": "pytest",
    "test:py:fast": "pytest -x",

    "// ===== COMBINED VALIDATION =====": "",
    "validate-all": "npm run lint:py && npm run format:py:check && npm run typecheck:py"
  }
}
```

**Check script exists helper:**

```bash
# Helper function to verify npm scripts exist
check_npm_script() {
  local script_name="$1"
  if ! npm run "$script_name" --silent 2>&1 | grep -q "Missing script"; then
    return 0
  else
    return 1
  fi
}

# Example usage
if ! check_npm_script "lint:py"; then
  echo "⚠️ WARNING: npm script 'lint:py' not found in package.json"
  echo "Add validation scripts (see docs)"
fi
```

---

## Python Tool Configuration

**Required Python packages:**

```bash
# Install validation tools
pip install ruff mypy pytest pytest-cov
```

**pyproject.toml configuration:**

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

---

## Error Handling Patterns

### Handle Missing Validation Scripts

```bash
# Check if validation script exists before running
if check_npm_script "lint:py"; then
  npm run lint:py || LINT_FAILED=1
else
  echo "⚠️ Skipping lint:py (script not found)"
fi
```

### Handle Missing Python Tools

```bash
# Check if tools are installed
if ! command -v ruff &> /dev/null; then
  echo "❌ ERROR: ruff not installed"
  echo "Install: pip install ruff"
  exit 1
fi

if ! command -v mypy &> /dev/null; then
  echo "❌ ERROR: mypy not installed"
  echo "Install: pip install mypy"
  exit 1
fi
```

### Handle Agent Timeout

```bash
# If agent doesn't complete in reasonable time
AGENT_TIMEOUT=600  # 10 minutes

timeout $AGENT_TIMEOUT Task(...) || {
  echo "❌ ERROR: Fixer agent timed out after ${AGENT_TIMEOUT}s"
  echo "Possible causes:"
  echo "  • Too many errors to fix"
  echo "  • Agent stuck in loop"
  echo "  • Complex type errors requiring manual intervention"
  exit 1
}
```

---

## Integration Notes

### Phase 1 → Phase 2 Handoff

Phase 2 expects these artifacts from Phase 1:

- `.workflow/outputs/${ARGUMENTS}/phase1_results.json` - Implementation results
- Modified/created files as specified in implementation plan
- Clean git working directory (all changes staged/committed)

### Phase 2 → Phase 3 Handoff

Phase 2 provides these artifacts for Phase 3 (Documentation/Post-Mortem):

- `.workflow/outputs/${ARGUMENTS}/validation/validation_status.json` - Final status
- `.workflow/outputs/${ARGUMENTS}/validation/*.log` - All validation logs
- `.workflow/outputs/${ARGUMENTS}/validation/fix_attempt_*.json` - Fix attempt results

---

## Validation Checklist

Before completing Phase 2:

- [ ] Python linting passed (Ruff)
- [ ] Python formatting passed (Ruff)
- [ ] Python type checking passed (mypy) - if type hints present
- [ ] Architecture validation passed (if configured)
- [ ] Contract validation passed (if configured)
- [ ] Test execution completed (optional, non-blocking)
- [ ] Validation status JSON written
- [ ] All validation logs captured
- [ ] Fix attempts documented (if retry loop used)
- [ ] Workflow blocked if max attempts exhausted
- [ ] Summary displayed to orchestrator

---

## Example Output

**Successful validation (first attempt):**

```
🔍 Phase 2: Validation

▸ Running Python linting (Ruff)...
  ✅ Linting passed

▸ Running Python formatting check (Ruff)...
  ✅ Formatting passed

▸ Running Python type checking (mypy)...
  ✅ Type checking passed

✅ Validation passed on first attempt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Phase 2 Complete: Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Validation Results:

  Linting:              ✅ passed
  Formatting:           ✅ passed
  Type checking:        ✅ passed

Validation artifacts:
  • Status:       .workflow/outputs/EPIC-007/validation/validation_status.json
  • Logs:         .workflow/outputs/EPIC-007/validation/*.log
```

**Validation with retry (2 attempts):**

```
🔍 Phase 2: Validation

▸ Running Python linting (Ruff)...
  ❌ Linting failed

▸ Running Python formatting check (Ruff)...
  ❌ Formatting failed

▸ Running Python type checking (mypy)...
  ❌ Type checking failed

⚠️ Validation failed - initiating retry loop

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 Fix Attempt 1/3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Deploying Build Fixer Agent...

Waiting for fixer agent to complete...

Fixer agent completed with status: passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Re-running validation after fixes...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Validation passed on attempt 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Phase 2 Complete: Validation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Validation Results:

  Linting:              ✅ passed
  Formatting:           ✅ passed
  Type checking:        ✅ passed

Fix attempts: 1/3

Validation artifacts:
  • Status:       .workflow/outputs/EPIC-007/validation/validation_status.json
  • Logs:         .workflow/outputs/EPIC-007/validation/*.log
  • Fix results:  .workflow/outputs/EPIC-007/validation/fix_attempt_*.json
```

**Workflow blocked (max attempts exhausted):**

```
🔍 Phase 2: Validation

[... initial validation failures ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 Fix Attempt 3/3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[... fixer agent attempts fixes ...]

❌ Validation still failing after attempt 3

  • Type checking: ❌ still failing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ WORKFLOW BLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Validation failed after 3 attempts.

Manual intervention required.

Review:
  • Error logs: .workflow/outputs/EPIC-007/validation/
  • Fix attempts: .workflow/outputs/EPIC-007/validation/fix_attempt_*.json

Common issues:
  • Missing dependencies (install with pip)
  • Unclear type requirements (check spec)
  • Architecture violations (review boundaries)
```

---

## End of Phase 2 Content

This content can be integrated into `.claude/commands/execute-workflow.md` as Phase 2.
