# Workflow Example: Complete Walkthrough

**Last Updated:** 2025-10-19
**Status:** Production Ready
**Location:** `~/tier1_workflow_global/implementation/`

---

## Overview

This document provides a complete, step-by-step example of using the Tier 1 workflow command to implement a feature from specification to commit.

**Example Feature:** Add email validation to user registration

**Time Estimate:** 15-20 minutes (including refinement)

---

## Prerequisites

Before starting:
- Claude Code installed and configured
- Workflow command installed (`/execute-workflow` available)
- Project has `.tasks/` directory structure
- Package.json has validation scripts
- Agent briefings present in `.claude/agent_briefings/`

---

## Step 1: Create Epic Specification

**Command:**
```bash
/spec-epic
```

**User Input:**

*Claude prompts:* "What feature would you like to specify?"

*User provides:*
```
Add email validation to user registration.

Requirements:
- Validate email format before creating user account
- Reject invalid emails with clear error message
- Support common email formats (RFC 5322)
- Integration with existing auth_routes.py
- Custom exception for invalid emails
```

**Expected Output:**

```
✅ Epic created: EPIC-042

Location: .tasks/backlog/EPIC-042-add-email-validation/spec.md

Summary:
- Title: Add email validation to user registration
- Requirements: 5 items
- Acceptance criteria: 3 items
- Technical considerations: Noted

Next steps:
1. Review spec.md
2. Run /refine-epic EPIC-042 to generate implementation plan
```

**Verify Spec:**
```bash
cat .tasks/backlog/EPIC-042-add-email-validation/spec.md
```

**Expected Content:**
```markdown
# Epic: Add Email Validation to User Registration

## Overview
Implement email validation for user registration to ensure only valid email addresses are accepted.

## Requirements

### Functional Requirements
1. Validate email format using regex pattern (RFC 5322 compliant)
2. Reject registration attempts with invalid emails
3. Return clear error message to user
4. Validate before database insertion

### Non-Functional Requirements
5. Validation should complete in <50ms
6. Error messages must be user-friendly

## Acceptance Criteria

1. ✅ Valid emails pass validation:
   - user@example.com ✅
   - firstname.lastname@company.co.uk ✅
   - user+tag@example.com ✅

2. ✅ Invalid emails are rejected:
   - @example.com ❌
   - user@.com ❌
   - user@example ❌
   - user example@test.com ❌

3. ✅ Error message is returned:
   - HTTP 400 status
   - Error message: "Invalid email format: {email}"

## Technical Considerations

- Use Python regex library for validation
- Create custom EmailValidationError exception
- Integration point: src/backend/api/auth_routes.py (POST /register endpoint)
- Service layer: Add validation to UserService

## Dependencies

- Existing UserService (src/backend/services/user_service.py)
- Existing auth routes (src/backend/api/auth_routes.py)
- Existing User schema (src/backend/schemas/user.py)

## Risks

- Overly strict validation may reject valid emails
- Regex performance on long strings

## Estimated Effort

- Development: 2-3 hours
- Testing: 1 hour
- Code review: 30 minutes
```

---

## Step 2: Refine Epic (Generate Implementation Plan)

**Command:**
```bash
/refine-epic EPIC-042
```

**Expected Output:**

```
🔍 Refining epic: EPIC-042

Reading spec.md...
Analyzing requirements...
Generating architecture design...

✅ architecture.md created

Key design decisions:
- Create EmailValidator class (src/backend/validators/email_validator.py)
- Custom exception: EmailValidationError
- Integration: UserService.create_user() method
- Error handling: Catch exception in auth_routes.py

Generating implementation plan...

✅ file-tasks.md created

Files to create: 2
Files to modify: 3

Summary:
- Create: email_validator.py, exceptions.py
- Modify: user_service.py, auth_routes.py, user.py

Epic ready for execution.

Next step: /execute-workflow EPIC-042
```

**Verify Architecture:**
```bash
cat .tasks/backlog/EPIC-042-add-email-validation/architecture.md
```

**Expected Content:**
```markdown
# Architecture: Add Email Validation to User Registration

## Design Overview

Add email validation layer to user registration flow:
1. API route receives registration request
2. UserService validates email format
3. If invalid, raise EmailValidationError
4. If valid, proceed with user creation

## Components

### 1. Email Validator (NEW)

**File:** `src/backend/validators/email_validator.py`

**Responsibility:** Validate email format using regex

**Methods:**
- `validate_email(email: str) -> bool`
- `is_valid_email_format(email: str) -> bool`

**Dependencies:** Python `re` module

### 2. Custom Exceptions (NEW)

**File:** `src/backend/exceptions.py`

**Responsibility:** Define domain-specific exceptions

**Exceptions:**
- `EmailValidationError` - Raised when email format is invalid

### 3. UserService (MODIFY)

**File:** `src/backend/services/user_service.py`

**Changes:**
- Import EmailValidator and EmailValidationError
- Call `validate_email()` in `create_user()` method
- Raise EmailValidationError if validation fails

### 4. Auth Routes (MODIFY)

**File:** `src/backend/api/auth_routes.py`

**Changes:**
- Import EmailValidationError
- Add try/except in POST /register endpoint
- Catch EmailValidationError and return HTTP 400

### 5. User Schema (MODIFY)

**File:** `src/backend/schemas/user.py`

**Changes:**
- Add Pydantic email validation (EmailStr field type)
- Provides secondary validation at schema level

## Data Flow

```
1. POST /api/register
   ↓
2. auth_routes.py (parse request)
   ↓
3. UserService.create_user()
   ↓
4. EmailValidator.validate_email() ← Validation happens here
   ↓
5a. Valid → Continue to database
5b. Invalid → Raise EmailValidationError
   ↓
6. auth_routes.py catches exception
   ↓
7. Return HTTP 400 with error message
```

## Design Decisions

### Decision 1: Separate Validator Class

**Why:**
- Single Responsibility Principle
- Reusable across services
- Easier to test

**Alternative:** Inline validation in UserService
**Trade-off:** Less reusable, harder to test

### Decision 2: Custom Exception

**Why:**
- Domain-specific error handling
- Clear error type distinction
- Easier to catch and handle

**Alternative:** Raise ValueError or HTTPException directly
**Trade-off:** Less semantic, harder to distinguish error types

### Decision 3: Service Layer Validation

**Why:**
- Business logic belongs in service layer
- API routes stay thin
- Consistent with project patterns

**Alternative:** Validate in Pydantic schema only
**Trade-off:** Limited control over error messages

## Testing Strategy

1. Unit tests for EmailValidator
2. Unit tests for UserService (mock validator)
3. Integration tests for auth routes

## Security Considerations

- Regex must be safe (no ReDoS vulnerability)
- Error messages should not leak sensitive data
- Rate limiting on registration endpoint (out of scope)

## Performance Considerations

- Regex validation: <50ms (acceptable)
- No database queries during validation (fast)
```

**Verify Implementation Plan:**
```bash
cat .tasks/backlog/EPIC-042-add-email-validation/implementation-details/file-tasks.md
```

**Expected Content:**
```markdown
# Implementation Plan: EPIC-042 - Add Email Validation

## Files to Create

### `src/backend/validators/email_validator.py`

**Purpose:** Email format validation using regex

**Requirements:**
- Create `EmailValidator` class
- Implement `validate_email(email: str) -> bool` method
- Use regex pattern for RFC 5322 compliance
- Raise `EmailValidationError` for invalid emails

**Implementation Details:**
```python
import re
from src.backend.exceptions import EmailValidationError

class EmailValidator:
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format. Raises EmailValidationError if invalid."""
        if not re.match(EmailValidator.EMAIL_REGEX, email):
            raise EmailValidationError(f"Invalid email format: {email}")
        return True
```

**Dependencies:**
- `re` module (Python standard library)
- `EmailValidationError` from `src.backend.exceptions`

---

### `src/backend/exceptions.py`

**Purpose:** Custom domain exceptions

**Requirements:**
- Create `EmailValidationError` exception class
- Inherit from `Exception`
- Accept error message as parameter

**Implementation Details:**
```python
class EmailValidationError(Exception):
    """Raised when email validation fails."""
    pass
```

**Dependencies:** None

---

## Files to Modify

### `src/backend/services/user_service.py`

**Changes:**
- Import `EmailValidator` from `src.backend.validators.email_validator`
- Import `EmailValidationError` from `src.backend.exceptions`
- Modify `create_user()` method to validate email before creating user

**Location:** Line 25 (inside `create_user()` method, before database insertion)

**Code to Add:**
```python
# Validate email format
EmailValidator.validate_email(user_data.email)
```

**Full Modified Method:**
```python
async def create_user(self, user_data: UserCreate) -> User:
    """Create new user with email validation."""
    # Validate email format
    EmailValidator.validate_email(user_data.email)

    # Create user (existing code)
    user = User(**user_data.dict())
    self.db.add(user)
    await self.db.commit()
    await self.db.refresh(user)
    return user
```

**Preserve:**
- Existing error handling
- Database transaction logic
- Type hints

---

### `src/backend/api/auth_routes.py`

**Changes:**
- Import `EmailValidationError` from `src.backend.exceptions`
- Add try/except block in POST /register endpoint
- Catch `EmailValidationError` and return HTTP 400

**Location:** Line 35 (POST /register endpoint)

**Code to Add:**
```python
try:
    user = await service.create_user(user_data)
    return user
except EmailValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

**Preserve:**
- Existing imports
- Other endpoints
- Dependency injection

---

### `src/backend/schemas/user.py`

**Changes:**
- Import `EmailStr` from Pydantic
- Change `email` field type from `str` to `EmailStr`

**Location:** Line 10 (UserCreate schema)

**Code to Change:**
```python
# Before
email: str

# After
email: EmailStr  # Pydantic email validation
```

**Preserve:**
- Other fields
- Schema structure
- Existing validators

---

## Implementation Order

1. Create `src/backend/exceptions.py` (no dependencies)
2. Create `src/backend/validators/email_validator.py` (depends on exceptions)
3. Modify `src/backend/services/user_service.py` (uses validator)
4. Modify `src/backend/api/auth_routes.py` (catches exception)
5. Modify `src/backend/schemas/user.py` (secondary validation)

## Validation Checklist

- [ ] All files created/modified as specified
- [ ] EmailValidator.validate_email() raises EmailValidationError for invalid emails
- [ ] UserService.create_user() calls EmailValidator.validate_email()
- [ ] auth_routes.py catches EmailValidationError and returns HTTP 400
- [ ] Type hints present on all new functions
- [ ] No syntax errors
- [ ] Linting passes (ruff check)
- [ ] Type checking passes (mypy)
```

---

## Step 3: Review Implementation Plan

**Manual Review:**
```bash
# Check all required files
cat .tasks/backlog/EPIC-042-add-email-validation/spec.md
cat .tasks/backlog/EPIC-042-add-email-validation/architecture.md
cat .tasks/backlog/EPIC-042-add-email-validation/implementation-details/file-tasks.md
```

**Verify:**
- [ ] File paths match project structure
- [ ] Instructions are clear and specific
- [ ] Dependencies are documented
- [ ] Implementation order makes sense
- [ ] No critical files missing

**If issues found:**
- Edit file-tasks.md manually
- Or re-run `/refine-epic EPIC-042` with clarifications

---

## Step 4: Execute Workflow

**Command:**
```bash
/execute-workflow EPIC-042
```

**Expected Output:**

### Phase 0: Preflight

```
🚀 Phase 0: Preflight

✅ Epic ready: EPIC-042
   - spec.md found
   - architecture.md found
   - file-tasks.md found

✅ Git working directory clean

🔀 Analyzing parallel opportunities...
   - File count: 5
   - Domain count: 1 (backend only)
   - File overlap: 0.0%

➡️ Sequential execution
Reason: Too few domains (1 < 2)

Proceeding to Phase 1A (Sequential Implementation)...
```

### Phase 1: Implementation

```
🔨 Phase 1: Implementation

Deploying implementation agent...

Agent: implementation-agent-v1
Domain: backend
Briefings:
  - backend_implementation.md
  - project_architecture.md

Reading prescriptive plan...
Parsing file-tasks.md...

Files to create: 2
Files to modify: 3

Creating src/backend/exceptions.py...
✅ Created

Creating src/backend/validators/email_validator.py...
✅ Created

Modifying src/backend/services/user_service.py...
✅ Modified (added email validation)

Modifying src/backend/api/auth_routes.py...
✅ Modified (added error handling)

Modifying src/backend/schemas/user.py...
✅ Modified (changed email field to EmailStr)

Running syntax check...
✅ No syntax errors

Running lint check...
✅ Linting passed

Writing implementation results...
✅ Results written to .workflow/outputs/EPIC-042/phase1_results.json

✅ Phase 1 Complete

Files created: 2
  - src/backend/exceptions.py
  - src/backend/validators/email_validator.py

Files modified: 3
  - src/backend/services/user_service.py
  - src/backend/api/auth_routes.py
  - src/backend/schemas/user.py

Duration: 3m 24s
```

### Phase 2: Validation

```
🔍 Phase 2: Validation

Running validation: npm run validate
Command: ruff check src/backend/ && mypy src/backend/

Running ruff check...
✅ Linting passed (0 errors)

Running mypy...
✅ Type checking passed (0 errors)

✅ Validation passed

Results: .workflow/outputs/EPIC-042/validation_results.json

Duration: 18s
```

### Phase 5: Commit & Cleanup

```
📦 Phase 5: Commit & Cleanup

Staging files:
  - src/backend/exceptions.py
  - src/backend/validators/email_validator.py
  - src/backend/services/user_service.py
  - src/backend/api/auth_routes.py
  - src/backend/schemas/user.py

Creating commit...

Commit message:
────────────────────────────────
feat(EPIC-042): Add email validation to user registration

Implemented email format validation with custom exception
and integration into UserService and auth routes.

Files:
- Created: src/backend/exceptions.py (EmailValidationError)
- Created: src/backend/validators/email_validator.py (EmailValidator)
- Modified: src/backend/services/user_service.py (validate_email call)
- Modified: src/backend/api/auth_routes.py (error handling)
- Modified: src/backend/schemas/user.py (EmailStr field)

🤖 Generated with Claude Code
https://claude.com/claude-code

Co-Authored-By: Claude <noreply@anthropic.com>
────────────────────────────────

✅ Commit created: 7f3a9b2

Moving epic to completed/...
✅ Epic moved: EPIC-042-add-email-validation

Cleaning up workflow artifacts...
✅ Artifacts preserved in .workflow/outputs/EPIC-042/

✅ Workflow Complete: EPIC-042

Total duration: 4m 12s
```

---

## Step 5: Review Results

### View Commit

**Command:**
```bash
git log -1 -p
```

**Expected Output:**
```
commit 7f3a9b2c8d1e4f5a6b7c8d9e0f1a2b3c4d5e6f7
Author: Andreas Spannbauer <andreas.spannbauer@example.com>
Date:   Sat Oct 19 15:30:42 2025 +0200

    feat(EPIC-042): Add email validation to user registration

    Implemented email format validation with custom exception
    and integration into UserService and auth routes.

    Files:
    - Created: src/backend/exceptions.py (EmailValidationError)
    - Created: src/backend/validators/email_validator.py (EmailValidator)
    - Modified: src/backend/services/user_service.py (validate_email call)
    - Modified: src/backend/api/auth_routes.py (error handling)
    - Modified: src/backend/schemas/user.py (EmailStr field)

    🤖 Generated with Claude Code
    https://claude.com/claude-code

    Co-Authored-By: Claude <noreply@anthropic.com>

diff --git a/src/backend/exceptions.py b/src/backend/exceptions.py
new file mode 100644
index 0000000..a1b2c3d
--- /dev/null
+++ b/src/backend/exceptions.py
@@ -0,0 +1,6 @@
+"""Custom domain exceptions."""
+
+class EmailValidationError(Exception):
+    """Raised when email validation fails."""
+    pass

diff --git a/src/backend/validators/email_validator.py b/src/backend/validators/email_validator.py
new file mode 100644
index 0000000..d4e5f6a
--- /dev/null
+++ b/src/backend/validators/email_validator.py
@@ -0,0 +1,15 @@
+"""Email validation utilities."""
+import re
+from src.backend.exceptions import EmailValidationError
+
+class EmailValidator:
+    """Email format validator using regex."""
+
+    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
+
+    @staticmethod
+    def validate_email(email: str) -> bool:
+        """Validate email format. Raises EmailValidationError if invalid."""
+        if not re.match(EmailValidator.EMAIL_REGEX, email):
+            raise EmailValidationError(f"Invalid email format: {email}")
+        return True

diff --git a/src/backend/services/user_service.py b/src/backend/services/user_service.py
index b7c8d9e..f1a2b3c 100644
--- a/src/backend/services/user_service.py
+++ b/src/backend/services/user_service.py
@@ -2,6 +2,8 @@
 from sqlalchemy.ext.asyncio import AsyncSession
 from src.backend.models.user import User
 from src.backend.schemas.user import UserCreate
+from src.backend.validators.email_validator import EmailValidator
+from src.backend.exceptions import EmailValidationError

 class UserService:
     """User management service."""
@@ -12,6 +14,9 @@ class UserService:
     async def create_user(self, user_data: UserCreate) -> User:
         """Create new user with email validation."""
+        # Validate email format
+        EmailValidator.validate_email(user_data.email)
+
         user = User(**user_data.dict())
         self.db.add(user)
         await self.db.commit()

diff --git a/src/backend/api/auth_routes.py b/src/backend/api/auth_routes.py
index c3d4e5f..a6b7c8d 100644
--- a/src/backend/api/auth_routes.py
+++ b/src/backend/api/auth_routes.py
@@ -3,6 +3,7 @@ from fastapi import APIRouter, Depends, HTTPException
 from sqlalchemy.ext.asyncio import AsyncSession
 from src.backend.services.user_service import UserService
 from src.backend.schemas.user import UserCreate, UserResponse
+from src.backend.exceptions import EmailValidationError
 from src.backend.database import get_db

 router = APIRouter(prefix="/api/auth", tags=["authentication"])
@@ -13,8 +14,12 @@ async def register(
     user_data: UserCreate,
     db: AsyncSession = Depends(get_db)
 ):
-    service = UserService(db)
-    user = await service.create_user(user_data)
-    return user
+    try:
+        service = UserService(db)
+        user = await service.create_user(user_data)
+        return user
+    except EmailValidationError as e:
+        raise HTTPException(status_code=400, detail=str(e))

diff --git a/src/backend/schemas/user.py b/src/backend/schemas/user.py
index d9e0f1a..b2c3d4e 100644
--- a/src/backend/schemas/user.py
+++ b/src/backend/schemas/user.py
@@ -1,10 +1,10 @@
 """User schemas for request/response validation."""
-from pydantic import BaseModel
+from pydantic import BaseModel, EmailStr

 class UserCreate(BaseModel):
     """User creation schema."""
     username: str
-    email: str
+    email: EmailStr
     password: str

 class UserResponse(BaseModel):
```

### View Implementation Results

**Command:**
```bash
cat .workflow/outputs/EPIC-042/phase1_results.json
```

**Expected Output:**
```json
{
  "status": "success",
  "epic_id": "EPIC-042",
  "agent_type": "implementation-agent-v1",
  "execution_mode": "sequential",
  "files_created": [
    "src/backend/exceptions.py",
    "src/backend/validators/email_validator.py"
  ],
  "files_modified": [
    "src/backend/services/user_service.py",
    "src/backend/api/auth_routes.py",
    "src/backend/schemas/user.py"
  ],
  "issues_encountered": [],
  "clarifications_needed": [],
  "completion_timestamp": "2025-10-19T15:27:18Z"
}
```

### View Validation Results

**Command:**
```bash
cat .workflow/outputs/EPIC-042/validation_results.json
```

**Expected Output:**
```json
{
  "status": "success",
  "epic_id": "EPIC-042",
  "validation_attempts": 1,
  "final_result": "passed",
  "errors_found": [],
  "auto_fixes_applied": false,
  "validation_command": "ruff check src/backend/ && mypy src/backend/",
  "stdout": "All checks passed!",
  "stderr": "",
  "completion_timestamp": "2025-10-19T15:27:36Z"
}
```

---

## Step 6: Verify Epic Moved

**Command:**
```bash
ls .tasks/completed/ | grep EPIC-042
```

**Expected Output:**
```
EPIC-042-add-email-validation
```

**Verify epic no longer in backlog:**
```bash
ls .tasks/backlog/ | grep EPIC-042
# Should return no results
```

---

## Step 7: Test Implementation (Manual)

**Test Valid Emails:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "user@example.com", "password": "secret123"}'

# Expected: HTTP 200, user created
```

**Test Invalid Emails:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "@example.com", "password": "secret123"}'

# Expected: HTTP 400, error message: "Invalid email format: @example.com"
```

---

## Step 8: Push to Remote

**Command:**
```bash
git push origin main
```

**Expected Output:**
```
Enumerating objects: 15, done.
Counting objects: 100% (15/15), done.
Delta compression using up to 8 threads
Compressing objects: 100% (8/8), done.
Writing objects: 100% (8/8), 1.23 KiB | 1.23 MiB/s, done.
Total 8 (delta 5), reused 0 (delta 0)
remote: Resolving deltas: 100% (5/5), completed with 3 local objects.
To github.com:yourorg/yourproject.git
   6e2f1d3..7f3a9b2  main -> main
```

---

## Summary

**What We Accomplished:**

1. ✅ Created epic specification (EPIC-042)
2. ✅ Generated architecture design
3. ✅ Generated prescriptive implementation plan
4. ✅ Executed automated workflow
5. ✅ Created 2 new files (exceptions.py, email_validator.py)
6. ✅ Modified 3 existing files (user_service.py, auth_routes.py, user.py)
7. ✅ Passed validation (lint + type check)
8. ✅ Created conventional commit
9. ✅ Moved epic to completed/
10. ✅ Pushed to remote

**Time Breakdown:**

- Epic creation: 2 minutes
- Epic refinement: 3 minutes
- Review: 2 minutes
- Workflow execution: 4 minutes
- Review and push: 2 minutes
- **Total: 13 minutes**

**Manual Intervention:** 0 steps (fully automated)

---

## What If Something Goes Wrong?

### Validation Fails

**Scenario:** Validation fails after 3 attempts

**Action:**
1. Review validation errors: `cat .workflow/outputs/EPIC-042/validation_errors.log`
2. Fix errors manually
3. Run validation: `npm run validate`
4. Commit fixes: `git add . && git commit -m "fix(EPIC-042): Fix validation errors"`

### Epic Not Ready

**Scenario:** Missing spec.md, architecture.md, or file-tasks.md

**Action:**
1. Run refinement: `/refine-epic EPIC-042`
2. Verify files: `ls .tasks/backlog/EPIC-042-*/`
3. Re-run workflow: `/execute-workflow EPIC-042`

### Git Not Clean

**Scenario:** Uncommitted changes present

**Action:**
1. Commit changes: `git add . && git commit -m "WIP"`
2. Or stash: `git stash`
3. Re-run workflow: `/execute-workflow EPIC-042`

---

## Next Steps

**Explore More:**
- Read [WORKFLOW_INTEGRATION_GUIDE.md](./WORKFLOW_INTEGRATION_GUIDE.md) for setup details
- Read [WORKFLOW_CUSTOMIZATION.md](./WORKFLOW_CUSTOMIZATION.md) to customize for your project
- Read [WORKFLOW_TROUBLESHOOTING.md](./WORKFLOW_TROUBLESHOOTING.md) for more issues

**Try With Your Project:**
1. Install workflow command
2. Copy agent briefings to your project
3. Create a small epic (3-5 files)
4. Run workflow
5. Review results
6. Customize briefings based on your patterns

**Advanced Usage:**
- Try parallel execution (7+ files, 2+ domains)
- Customize validation scripts
- Add post-mortem agent for continuous improvement
