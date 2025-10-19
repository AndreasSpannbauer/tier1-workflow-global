# Week 4 Testing Guide

## Overview

This guide covers testing procedures for Week 4 features:
- Validation phase with retry loop (max 3 attempts)
- Build fixer agent integration during validation
- Post-mortem analysis generation (Phase 6)

## Prerequisites

**Required Setup**:
- [ ] Workflow command installed (`/workflow` available)
- [ ] Test project with TypeScript/tests configured
- [ ] Git repository initialized
- [ ] Build scripts configured (package.json)

**Verification**:
```bash
# Check workflow command exists
ls ~/.claude/commands/workflow.md

# Check test project structure
cd /path/to/test-project
ls package.json tsconfig.json
ls src/ tests/
```

## Test Procedures

### Test 1: Validation Retry Loop

**Objective**: Verify validation phase retries up to 3 times on failures.

**Steps**:

1. **Introduce intentional validation error**:
```bash
# Edit a test file to create failing test
echo 'test("intentional fail", () => { expect(1).toBe(2); });' >> tests/validation-test.spec.ts
```

2. **Run workflow**:
```bash
/workflow analyze
# When prompted for goal: "Add simple validation test feature"
```

3. **During validation phase, verify**:
- [ ] Validation attempt 1 runs
- [ ] Test failure detected
- [ ] Build fixer agent deploys automatically
- [ ] Validation attempt 2 runs (if agent didn't fix)
- [ ] Validation attempt 3 runs (if still failing)
- [ ] After 3 attempts, validation fails gracefully

**Expected Output Pattern**:
```
=== Phase 5: Validation ===
Attempt 1/3: Running build and tests...
❌ Validation failed: [error details]

Deploying build fixer agent...
🔧 Build Fixer Agent analyzing failure...

Attempt 2/3: Running build and tests...
[repeat if needed]

Attempt 3/3: Running build and tests...
❌ Validation failed after 3 attempts
```

**Success Criteria**:
- [ ] Retry loop executes (1-3 attempts)
- [ ] Build fixer agent deploys on failure
- [ ] Clear attempt counter shown (X/3)
- [ ] Graceful failure after max attempts

### Test 2: Build Fixer Agent Integration

**Objective**: Verify build fixer agent automatically fixes validation errors.

**Steps**:

1. **Introduce fixable validation error**:
```bash
# Create type error
echo 'const x: number = "string";' >> src/validation-error.ts
```

2. **Run workflow**:
```bash
/workflow analyze
# Goal: "Add type-safe validation error file"
```

3. **During validation phase, observe**:
- [ ] Validation attempt 1 fails (type error)
- [ ] Build fixer agent deploys
- [ ] Agent analyzes TypeScript error
- [ ] Agent fixes the error
- [ ] Validation attempt 2 succeeds

**Expected Output Pattern**:
```
Attempt 1/3: Running build and tests...
❌ Build failed: Type 'string' is not assignable to type 'number'

Deploying build fixer agent...
🔧 Analyzing error: [error details]
📝 Proposed fix: Change type annotation or value
✅ Applied fix to src/validation-error.ts

Attempt 2/3: Running build and tests...
✅ Validation passed!
```

**Success Criteria**:
- [ ] Agent identifies error type
- [ ] Agent proposes fix
- [ ] Fix is applied
- [ ] Subsequent validation succeeds

### Test 3: Post-Mortem Generation

**Objective**: Verify Phase 6 generates comprehensive post-mortem report.

**Steps**:

1. **Complete full workflow** (with at least one validation retry):
```bash
/workflow analyze
# Goal: "Add feature that requires validation fix"
# Let workflow run through all phases
```

2. **After workflow completion, verify**:
- [ ] Phase 6 executes
- [ ] Post-mortem report generated
- [ ] Report saved to `tier1_postmortem_YYYYMMDD_HHMMSS.md`

3. **Check report contents**:
```bash
# Find latest post-mortem
ls -lt tier1_postmortem_*.md | head -1

# View report
cat tier1_postmortem_YYYYMMDD_HHMMSS.md
```

**Expected Report Sections**:
- [ ] Executive Summary
- [ ] What Went Well
- [ ] What Went Wrong
- [ ] Validation Attempts Summary (if retries occurred)
- [ ] Metrics (time per phase, total duration)
- [ ] Action Items for Next Iteration

**Success Criteria**:
- [ ] Report file created
- [ ] All sections populated
- [ ] Validation retry details included
- [ ] Metrics are accurate
- [ ] Actionable insights provided

### Test 4: Validation Max Attempts

**Objective**: Verify workflow stops after 3 validation attempts.

**Steps**:

1. **Introduce unfixable validation error**:
```bash
# Create runtime error in test
echo 'test("unfixable", () => { throw new Error("Unfixable"); });' >> tests/unfixable.spec.ts
```

2. **Run workflow**:
```bash
/workflow analyze
# Goal: "Add unfixable test feature"
```

3. **During validation phase, verify**:
- [ ] Attempt 1/3 runs and fails
- [ ] Build fixer agent tries to fix
- [ ] Attempt 2/3 runs and fails
- [ ] Build fixer agent tries again
- [ ] Attempt 3/3 runs and fails
- [ ] Workflow stops validation gracefully

4. **Check post-mortem**:
- [ ] Post-mortem generated despite validation failure
- [ ] Post-mortem includes validation failure analysis

**Expected Output Pattern**:
```
Attempt 1/3: Running build and tests...
❌ Test failed: Unfixable error

Deploying build fixer agent...
🔧 Attempting fix...

Attempt 2/3: Running build and tests...
❌ Test failed: Unfixable error

Deploying build fixer agent...
🔧 Attempting fix...

Attempt 3/3: Running build and tests...
❌ Test failed: Unfixable error

⚠️ Validation failed after 3 attempts
Proceeding to post-mortem analysis...

=== Phase 6: Post-Mortem ===
```

**Success Criteria**:
- [ ] Exactly 3 attempts executed
- [ ] No 4th attempt occurs
- [ ] Workflow doesn't hang
- [ ] Post-mortem still generated
- [ ] Failure reason documented

## Verification Checklist

After running all tests:

**Validation Phase**:
- [ ] Retry loop works (1-3 attempts)
- [ ] Attempt counter accurate
- [ ] Max attempts enforced
- [ ] Graceful failure handling

**Build Fixer Agent**:
- [ ] Auto-deploys on validation failure
- [ ] Analyzes errors correctly
- [ ] Proposes fixes
- [ ] Applies fixes successfully

**Post-Mortem**:
- [ ] Always generated (success or failure)
- [ ] Includes all required sections
- [ ] Validation retry details captured
- [ ] Metrics accurate
- [ ] File saved correctly

## Troubleshooting

### Issue: Validation doesn't retry

**Symptoms**: Only 1 validation attempt occurs

**Checks**:
```bash
# Verify workflow command has retry loop logic
grep -A 20 "Attempt 1/3" ~/.claude/commands/workflow.md
```

**Fix**: Update workflow command to include retry loop

### Issue: Build fixer agent not deploying

**Symptoms**: Validation fails but no agent appears

**Checks**:
```bash
# Check agent exists
ls ~/.claude/agents/build-fixer.md

# Verify deployment code in workflow
grep "build-fixer" ~/.claude/commands/workflow.md
```

**Fix**: Ensure workflow deploys agent on validation failure

### Issue: Post-mortem not generated

**Symptoms**: No `tier1_postmortem_*.md` file created

**Checks**:
```bash
# Check Phase 6 exists in workflow
grep -A 10 "Phase 6" ~/.claude/commands/workflow.md

# Check current directory
pwd  # Should be project root
```

**Fix**: Verify Phase 6 executes after validation (even on failure)

### Issue: Validation hangs after 3 attempts

**Symptoms**: Workflow doesn't exit after max attempts

**Checks**:
```bash
# Check max attempts logic
grep -A 5 "max.*attempt" ~/.claude/commands/workflow.md
```

**Fix**: Ensure retry loop has proper exit condition

## Expected Test Duration

- Test 1 (Validation Retry): ~5-10 minutes
- Test 2 (Build Fixer): ~3-5 minutes
- Test 3 (Post-Mortem): ~2-3 minutes (part of full workflow)
- Test 4 (Max Attempts): ~10-15 minutes

**Total**: ~30-45 minutes for complete test suite

## Next Steps

After successful testing:
1. Document any issues found
2. Update workflow command if needed
3. Run tests on multiple projects
4. Validate post-mortem insights are actionable
5. Proceed to Week 5 features (if applicable)
