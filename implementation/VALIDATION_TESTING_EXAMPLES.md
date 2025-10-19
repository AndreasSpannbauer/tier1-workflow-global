# Validation Testing Examples

## Overview

This document provides detailed code examples and scenarios for testing Week 4 validation features:
- Validation retry loop behavior
- Build fixer agent integration
- Post-mortem report generation

## Test Scenario 1: Type Error (Fixable)

**Purpose**: Verify build fixer agent can fix TypeScript type errors.

### Setup

Create a file with intentional type error:

```typescript
// src/type-error-test.ts
export function processData(value: number): string {
  // Type error: returning number instead of string
  return value * 2;
}

export const config = {
  timeout: "5000"  // Type error: should be number
};

interface User {
  id: number;
  name: string;
}

const user: User = {
  id: "123",  // Type error: should be number
  name: "Test"
};
```

### Expected Validation Flow

**Attempt 1**:
```
npm run build
❌ Build failed with 3 errors:

src/type-error-test.ts:3:10 - error TS2322: Type 'number' is not assignable to type 'string'.
src/type-error-test.ts:7:3 - error TS2322: Type 'string' is not assignable to type 'number'.
src/type-error-test.ts:16:3 - error TS2322: Type 'string' is not assignable to type 'number'.
```

**Build Fixer Agent Deploys**:
```
🔧 Build Fixer Agent analyzing errors...

Identified issues:
1. Function return type mismatch (line 3)
2. Config property type mismatch (line 7)
3. User property type mismatch (line 16)

Proposed fixes:
- Convert number to string in processData return
- Change config.timeout to number
- Change user.id to number
```

**Attempt 2** (after fixes):
```
npm run build
✅ Build successful!
```

### Verification

```bash
# Check that fixes were applied
cat src/type-error-test.ts

# Should show:
# - return (value * 2).toString();
# - timeout: 5000
# - id: 123
```

## Test Scenario 2: Failing Test (Auto-Fixable)

**Purpose**: Verify build fixer agent can fix test assertion errors.

### Setup

Create a test with wrong assertion:

```typescript
// tests/calculation.spec.ts
import { describe, it, expect } from 'vitest';

function add(a: number, b: number): number {
  return a + b;
}

describe('Math operations', () => {
  it('should add two numbers', () => {
    expect(add(2, 3)).toBe(6);  // Wrong: 2+3=5, not 6
  });

  it('should multiply correctly', () => {
    const multiply = (a: number, b: number) => a * b;
    expect(multiply(3, 4)).toBe(11);  // Wrong: 3*4=12, not 11
  });
});
```

### Expected Validation Flow

**Attempt 1**:
```
npm test
❌ Tests failed:

FAIL tests/calculation.spec.ts
  Math operations
    ✕ should add two numbers (3 ms)
    ✕ should multiply correctly (1 ms)

Expected: 6
Received: 5

Expected: 11
Received: 12
```

**Build Fixer Agent Deploys**:
```
🔧 Analyzing test failures...

Issue: Assertion expectations don't match actual results
- add(2, 3) returns 5, not 6
- multiply(3, 4) returns 12, not 11

Fix: Update assertions to match correct behavior
```

**Attempt 2** (after fixes):
```
npm test
✅ All tests passed! (2 passed, 2 total)
```

### Verification

```bash
# Check corrected assertions
grep "toBe" tests/calculation.spec.ts

# Should show:
# expect(add(2, 3)).toBe(5);
# expect(multiply(3, 4)).toBe(12);
```

## Test Scenario 3: Missing Import (Fixable)

**Purpose**: Verify build fixer agent handles import errors.

### Setup

Create file with missing imports:

```typescript
// src/import-error.ts
export function formatUser(user: User): string {
  return `${user.name} (${user.id})`;
}

export function validateEmail(email: string): boolean {
  return isEmail(email);  // isEmail not imported
}

export const logger = createLogger();  // createLogger not imported
```

### Expected Validation Flow

**Attempt 1**:
```
npm run build
❌ Build failed:

src/import-error.ts:1:35 - error TS2304: Cannot find name 'User'.
src/import-error.ts:6:10 - error TS2304: Cannot find name 'isEmail'.
src/import-error.ts:9:23 - error TS2304: Cannot find name 'createLogger'.
```

**Build Fixer Agent Deploys**:
```
🔧 Analyzing missing identifiers...

Missing imports detected:
- User: likely from './types' or '../types/user'
- isEmail: likely from 'validator' package
- createLogger: likely from './logger' or '../utils/logger'

Searching codebase for definitions...
Found: User in src/types/user.ts
Found: isEmail in node_modules/validator
Found: createLogger in src/utils/logger.ts

Adding imports...
```

**Attempt 2** (after fixes):
```
npm run build
✅ Build successful!
```

### Verification

```bash
# Check added imports
head -5 src/import-error.ts

# Should show:
# import { User } from './types/user';
# import { isEmail } from 'validator';
# import { createLogger } from './utils/logger';
```

## Test Scenario 4: Runtime Error (Unfixable)

**Purpose**: Verify max attempts (3) enforced when error is unfixable.

### Setup

Create test with runtime exception:

```typescript
// tests/runtime-error.spec.ts
import { describe, it } from 'vitest';

describe('Unfixable runtime error', () => {
  it('throws error during execution', () => {
    const obj: any = null;
    obj.property.nested.value = 123;  // Cannot read property of null
  });
});
```

### Expected Validation Flow

**Attempt 1**:
```
npm test
❌ Tests failed:

FAIL tests/runtime-error.spec.ts
  Unfixable runtime error
    ✕ throws error during execution (2 ms)

TypeError: Cannot read property 'property' of null
```

**Build Fixer Agent Deploys** (Attempt 1):
```
🔧 Analyzing error...

Issue: Null pointer exception
Proposed fix: Add null check

if (obj && obj.property) {
  obj.property.nested.value = 123;
}
```

**Attempt 2** (still fails - nested is also null):
```
npm test
❌ Tests failed:

TypeError: Cannot read property 'nested' of undefined
```

**Build Fixer Agent Deploys** (Attempt 2):
```
🔧 Analyzing error...

Issue: Nested null pointer
Proposed fix: Add deeper null checks
```

**Attempt 3** (still fails - fundamental design issue):
```
npm test
❌ Tests failed after 3 attempts

⚠️ Validation could not be completed automatically
Reason: Runtime error requires architectural change
```

### Verification

```bash
# Check attempts counter in logs
# Should show: "Attempt 3/3"
# Should NOT show: "Attempt 4/3"

# Verify post-mortem was still generated
ls -lt tier1_postmortem_*.md | head -1
```

## Test Scenario 5: Linting Error (Fixable)

**Purpose**: Verify build fixer agent handles ESLint/Prettier issues.

### Setup

Create file with linting violations:

```typescript
// src/linting-error.ts
export function badFormatting(  value:number  ):string{
const result=value*2
    return result.toString()
}

export const unused_variable = 123;  // Unused variable

function helper(){console.log("test")}  // No-console rule
```

### Expected Validation Flow

**Attempt 1**:
```
npm run lint
❌ Linting failed:

src/linting-error.ts
  1:31  error  Missing space before function parentheses
  1:38  error  Missing space after colon
  2:1   error  Expected indentation of 2 spaces
  7:14  error  'unused_variable' is assigned but never used
  9:20  error  Unexpected console statement (no-console)
```

**Build Fixer Agent Deploys**:
```
🔧 Fixing linting errors...

Running auto-fix: npm run lint -- --fix
Applied formatting fixes automatically

Remaining issues requiring manual intervention:
- Remove unused variable (line 7)
- Replace console.log with proper logger (line 9)
```

**Attempt 2** (after fixes):
```
npm run lint
✅ No linting errors!
```

### Verification

```bash
# Check auto-formatted code
cat src/linting-error.ts

# Should show proper spacing and indentation
# unused_variable should be removed
# console.log should be replaced or removed
```

## Post-Mortem Report Examples

### Example 1: Successful Validation (1 Retry)

```markdown
# Tier 1 Workflow Post-Mortem
Date: 2025-10-19 14:32:15

## Executive Summary
✅ Goal achieved: Add type-safe validation error file
Completed in 8m 45s with 1 validation retry

## What Went Well
- Spec analysis identified type safety requirements
- Implementation followed TypeScript best practices
- Build fixer agent successfully resolved type errors on first retry
- All tests passed after fix

## What Went Wrong
- Initial implementation had 3 type mismatches
- Missing type annotations in function signatures
- Config object used string instead of number

## Validation Attempts Summary
- Attempt 1: Failed (3 type errors)
- Attempt 2: Passed (build fixer agent applied fixes)

Build Fixer Agent Actions:
1. Converted function return value to string
2. Changed config.timeout from "5000" to 5000
3. Changed user.id from "123" to 123

## Metrics
- Total Duration: 8m 45s
- Phase 1 (Analysis): 2m 10s
- Phase 2 (Spec): 1m 30s
- Phase 3 (Plan): 1m 15s
- Phase 4 (Implementation): 2m 40s
- Phase 5 (Validation): 1m 10s (2 attempts)
- Phase 6 (Post-Mortem): 0m 15s

## Action Items
1. Add pre-commit type checking to catch errors earlier
2. Review TypeScript strict mode configuration
3. Document common type error patterns for team
```

### Example 2: Failed Validation (3 Retries)

```markdown
# Tier 1 Workflow Post-Mortem
Date: 2025-10-19 15:45:22

## Executive Summary
⚠️ Goal partially achieved: Add unfixable test feature
Validation failed after 3 attempts (15m 30s)

## What Went Well
- Spec correctly identified test requirements
- Implementation structure sound
- Build fixer agent attempted multiple fix strategies

## What Went Wrong
- Runtime error in test requires architectural change
- Null pointer exceptions cannot be auto-fixed
- Test design fundamentally flawed (testing null behavior incorrectly)

## Validation Attempts Summary
- Attempt 1: Failed (TypeError: Cannot read property 'property' of null)
  - Build fixer: Added null check for top-level object
- Attempt 2: Failed (TypeError: Cannot read property 'nested' of undefined)
  - Build fixer: Added deeper null checks
- Attempt 3: Failed (TypeError persisted)
  - Build fixer: Attempted optional chaining, still failed

## Metrics
- Total Duration: 15m 30s
- Phase 1 (Analysis): 2m 00s
- Phase 2 (Spec): 1m 20s
- Phase 3 (Plan): 1m 10s
- Phase 4 (Implementation): 3m 15s
- Phase 5 (Validation): 7m 45s (3 attempts)
- Phase 6 (Post-Mortem): 0m 20s

## Action Items
1. **CRITICAL**: Review test design approach for null handling
2. Refactor test to use proper mocks/stubs instead of null objects
3. Add validation rules to prevent null pointer test patterns
4. Update implementation guide with null safety best practices
5. Consider adding static analysis pre-checks before validation phase
```

## Validation Logs Reference

### Successful Retry Pattern
```
=== Phase 5: Validation ===
Running validation checks...

Attempt 1/3: Building project...
npm run build
❌ Build failed

Deploying build fixer agent...
🔧 Agent analyzing errors...
✅ Agent applied 3 fixes

Attempt 2/3: Building project...
npm run build
✅ Build successful!

Running tests...
npm test
✅ All tests passed!

Validation complete ✅
```

### Max Attempts Pattern
```
=== Phase 5: Validation ===
Running validation checks...

Attempt 1/3: Running tests...
❌ Test failed: Runtime error

Deploying build fixer agent...
🔧 Attempting fix...

Attempt 2/3: Running tests...
❌ Test failed: Runtime error persists

Deploying build fixer agent...
🔧 Attempting alternative fix...

Attempt 3/3: Running tests...
❌ Test failed: Runtime error persists

⚠️ Validation failed after maximum attempts (3/3)
Proceeding to post-mortem analysis...

=== Phase 6: Post-Mortem ===
```

## Common Testing Patterns

### Pattern 1: Verify Retry Counter
```bash
# Run workflow and capture output
/workflow analyze > workflow_output.log 2>&1

# Check retry attempts
grep "Attempt [0-9]/3" workflow_output.log

# Should show:
# Attempt 1/3
# Attempt 2/3
# (and possibly Attempt 3/3)
```

### Pattern 2: Verify Build Fixer Deployment
```bash
# Check agent was called
grep "build-fixer" workflow_output.log
grep "Agent analyzing" workflow_output.log

# Verify agent made changes
git diff  # Should show fixes applied
```

### Pattern 3: Verify Post-Mortem Content
```bash
# Find latest post-mortem
LATEST_PM=$(ls -t tier1_postmortem_*.md | head -1)

# Check required sections exist
grep "Executive Summary" "$LATEST_PM"
grep "Validation Attempts Summary" "$LATEST_PM"
grep "Metrics" "$LATEST_PM"
grep "Action Items" "$LATEST_PM"

# Check validation details included
grep "Attempt [0-9]:" "$LATEST_PM"
grep "Build Fixer Agent Actions:" "$LATEST_PM"
```

## Summary

This document provides:
- **5 test scenarios** covering different error types
- **Expected validation flows** for each scenario
- **2 post-mortem examples** (success and failure cases)
- **Validation log patterns** to recognize
- **Common testing patterns** for verification

Use these examples to thoroughly test Week 4 validation features before production deployment.
