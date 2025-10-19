# Week 3 Testing Examples

**Date:** 2025-10-19
**Purpose:** Concrete testing examples with complete code for all test scenarios
**Location:** `~/tier1_workflow_global/implementation/`

---

## Overview

This document provides complete, runnable code examples for all Week 3 test scenarios. Each example includes:

- Complete epic specification files
- Expected parallel detection output
- Full implementation code
- Validation commands
- Expected workflow execution trace

**Use Cases:**
- Manual testing during development
- Automated test suite inputs
- Reference implementations
- Training data for future improvements

---

## Example 1: Sequential Test Epic

### Overview

**Epic ID:** SEQ-001
**Title:** Add user email validation
**Files:** 2 (1 to create, 1 to modify)
**Domains:** 1 (backend)
**Expected Mode:** Sequential

### Complete Epic Files

**File:** `.tasks/backlog/SEQ-001/spec.md`

```markdown
---
epic_id: SEQ-001
title: Add user email validation
type: enhancement
priority: medium
estimated_hours: 2
---

# SEQ-001: Add user email validation

## Problem Statement

Users can currently submit invalid email addresses during registration, causing downstream issues with email delivery and user communication.

## Requirements

### Functional Requirements

- **FR-1:** Validate email format using industry-standard regex
  - Support standard formats: `user@domain.com`
  - Support subdomains: `user@mail.domain.com`
  - Support plus addressing: `user+tag@domain.com`
  - Reject invalid formats: missing @, multiple @, invalid characters

- **FR-2:** Return clear error messages for invalid emails
  - Message: "Invalid email format: {email}"
  - HTTP 400 status code
  - Include validation error in response body

- **FR-3:** Support multiple email providers
  - Gmail, Yahoo, Outlook, custom domains
  - No provider-specific validation

### Non-Functional Requirements

- **NFR-1:** Validation must be fast (<10ms)
- **NFR-2:** No external dependencies (use stdlib only)
- **NFR-3:** 100% unit test coverage for validator

## Acceptance Criteria

- [x] EmailValidator class created with validate() method
- [x] Regex pattern supports all standard email formats
- [x] Unit tests pass (100% coverage)
- [x] Integration with user routes complete
- [x] 400 status returned for invalid emails
- [x] Clear error messages in response

## Out of Scope

- Email deliverability checks (DNS/MX records)
- Disposable email detection
- Email normalization (case folding)

## Technical Notes

Use Python's `re` module for regex validation. Pattern based on RFC 5322 simplified.
```

---

**File:** `.tasks/backlog/SEQ-001/file-tasks.md`

```markdown
# File Tasks: SEQ-001

## Summary

Total files: 2
- To create: 1
- To modify: 1
- Domains: backend (1)

## Files to Create

### 1. src/validators/email_validator.py (50 lines)

**Purpose:** Email validation logic

**Contents:**
- EmailValidator class
- validate() method (returns bool, error_message)
- Regex pattern for standard email formats
- Error message generation

**Dependencies:**
- Python stdlib: `re`

**Test Coverage:**
- Valid emails: standard, subdomain, plus-addressing
- Invalid emails: missing @, multiple @, invalid chars

---

## Files to Modify

### 1. src/api/user_routes.py (+10 lines)

**Purpose:** Integrate email validation in user registration

**Changes:**
- Line 5: Import EmailValidator
- Line 45-50: Add validation before user creation
- Line 51-53: Return 400 on validation failure

**Affected Functions:**
- `create_user(request)` - Add validation step

**Dependencies:**
- New: EmailValidator

---

## Domain Analysis

### backend
Files: 2
- src/validators/email_validator.py (create)
- src/api/user_routes.py (modify)

**Reason:** Single domain (backend)
```

---

**File:** `.tasks/backlog/SEQ-001/architecture.md`

```markdown
# Architecture: SEQ-001

## System Context

```
User Request
    │
    ▼
User API (/users)
    │
    ├─► EmailValidator (NEW)
    │      └─► Regex Validation
    │
    └─► UserService
           └─► Database
```

## Changes

### Backend Layer

**New Components:**
- `src/validators/email_validator.py`
  - EmailValidator class
  - validate(email: str) -> tuple[bool, str]

**Modified Components:**
- `src/api/user_routes.py`
  - create_user() function
  - Add validation before UserService.create()

### Data Flow

1. User submits POST /users with email
2. user_routes.create_user() receives request
3. EmailValidator.validate() checks email format
4. If invalid: Return 400 with error message
5. If valid: Continue to UserService.create()

## Dependencies

### External Dependencies
- None (uses Python stdlib `re` module)

### Internal Dependencies
- user_routes.py depends on email_validator.py

## Domain Classification

All changes in **backend** domain:
- Validators: Backend validation layer
- API routes: Backend API layer

No changes in:
- Frontend (no UI changes)
- Database (no schema changes)
- Tests (separate task)

## Performance Impact

- Email validation: <10ms (regex operation)
- No database queries added
- No external API calls
- Negligible overall latency impact

## Security Considerations

- No sensitive data stored
- Validation happens server-side
- No client-side bypasses possible

## Rollback Plan

If validation causes issues:
1. Remove EmailValidator import from user_routes.py
2. Remove validation step from create_user()
3. Delete src/validators/email_validator.py
4. Deploy (backward compatible)
```

---

### Complete Implementation Code

**File:** `src/validators/email_validator.py`

```python
"""
Email validation module.

Provides EmailValidator class for validating email addresses
using industry-standard regex patterns.
"""

import re
from typing import Tuple


class EmailValidator:
    """Validate email addresses using regex patterns."""

    # RFC 5322 simplified pattern
    # Supports: user@domain.com, user+tag@mail.domain.com
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    @classmethod
    def validate(cls, email: str) -> Tuple[bool, str]:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid: bool, error_message: str)
            - If valid: (True, "")
            - If invalid: (False, "Invalid email format: {email}")

        Examples:
            >>> EmailValidator.validate("user@domain.com")
            (True, "")

            >>> EmailValidator.validate("invalid-email")
            (False, "Invalid email format: invalid-email")
        """
        if not email:
            return False, "Email is required"

        if not isinstance(email, str):
            return False, "Email must be a string"

        # Check for basic format issues
        if '@' not in email:
            return False, f"Invalid email format: {email} (missing @)"

        if email.count('@') > 1:
            return False, f"Invalid email format: {email} (multiple @)"

        # Apply regex pattern
        if not cls.EMAIL_PATTERN.match(email):
            return False, f"Invalid email format: {email}"

        return True, ""


# Convenience function
def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email using EmailValidator class."""
    return EmailValidator.validate(email)
```

---

**File:** `src/api/user_routes.py` (modified)

```python
"""User API routes."""

from flask import Blueprint, request, jsonify
from src.validators.email_validator import EmailValidator  # NEW IMPORT
from src.services.user_service import UserService

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user.

    Request Body:
        {
            "email": "user@example.com",
            "name": "John Doe",
            "password": "secret123"
        }

    Returns:
        201: User created successfully
        400: Validation error
        500: Server error
    """
    data = request.get_json()

    # Extract email
    email = data.get('email')

    # NEW: Validate email format
    is_valid, error_message = EmailValidator.validate(email)
    if not is_valid:
        return jsonify({
            'error': error_message,
            'field': 'email'
        }), 400

    # Continue with user creation
    try:
        user = UserService.create(
            email=email,
            name=data.get('name'),
            password=data.get('password')
        )
        return jsonify(user.to_dict()), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ... rest of file unchanged ...
```

---

### Expected Parallel Detection Output

```json
{
  "viable": false,
  "reason": "Too few files (2 < 8 minimum threshold)",
  "execution_mode": "sequential",
  "file_count": 2,
  "domain_count": 1,
  "domains": {
    "backend": [
      "src/validators/email_validator.py",
      "src/api/user_routes.py"
    ]
  },
  "thresholds": {
    "min_files": 8,
    "min_domains": 2
  },
  "metadata": {
    "epic_id": "SEQ-001",
    "epic_title": "Add user email validation",
    "analysis_timestamp": "2025-10-19T10:30:00Z"
  }
}
```

---

### Validation Commands

```bash
# 1. Run parallel detection
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  --epic-dir .tasks/backlog/SEQ-001 \
  --output .workflow/outputs/SEQ-001/parallel_analysis.json

# 2. Verify sequential mode
MODE=$(jq -r '.execution_mode' .workflow/outputs/SEQ-001/parallel_analysis.json)
echo "Execution mode: $MODE"
# Expected: "sequential"

# 3. Check file count
COUNT=$(jq -r '.file_count' .workflow/outputs/SEQ-001/parallel_analysis.json)
echo "File count: $COUNT"
# Expected: 2

# 4. Check domain count
DOMAINS=$(jq -r '.domain_count' .workflow/outputs/SEQ-001/parallel_analysis.json)
echo "Domain count: $DOMAINS"
# Expected: 1

# 5. Verify reason
REASON=$(jq -r '.reason' .workflow/outputs/SEQ-001/parallel_analysis.json)
echo "Reason: $REASON"
# Expected: "Too few files (2 < 8 minimum threshold)"
```

---

### Expected Workflow Execution Trace

```
=================================================================
Tier 1 Workflow: SEQ-001
=================================================================

Phase 0: Preflight
----------------------------------------------------------------------
✅ Epic directory found: .tasks/backlog/SEQ-001
✅ Required files present: spec.md, file-tasks.md, architecture.md
✅ Git status clean

Running parallel detection...
  File count: 2
  Domain count: 1
  Viable for parallel: false
  Reason: Too few files (2 < 8 minimum threshold)

Execution mode: SEQUENTIAL
Output: .workflow/outputs/SEQ-001/parallel_analysis.json

Phase 1A: Sequential Implementation
----------------------------------------------------------------------
Deploying implementation agent...

Agent Task: Implement SEQ-001
- Read spec.md
- Read file-tasks.md
- Create src/validators/email_validator.py
- Modify src/api/user_routes.py
- Run unit tests
- Write results

Agent execution complete.
✅ Files created: 1
✅ Files modified: 1

Phase 2: Validation
----------------------------------------------------------------------
Running linter... ✅ No errors
Running type checker... ✅ No errors
Running tests... ✅ All passed (12/12)

Phase 5: Commit & Cleanup
----------------------------------------------------------------------
Creating commit...
✅ Commit: abc1234 "feat: Add email validation (SEQ-001)"

Moving epic to completed...
✅ Moved: .tasks/backlog/SEQ-001 → .tasks/completed/SEQ-001

=================================================================
✅ Workflow Complete: SEQ-001
=================================================================
Duration: 3m 45s
Mode: Sequential
Files changed: 2
Status: Success
```

---

## Example 2: Parallel Test Epic (Clean Merge)

### Overview

**Epic ID:** PAR-CLEAN-001
**Title:** Complete user management system
**Files:** 14 (across 3 domains)
**Domains:** 3 (backend, frontend, database)
**Expected Mode:** Parallel

### Complete Epic Files

**File:** `.tasks/backlog/PAR-CLEAN-001/spec.md`

```markdown
---
epic_id: PAR-CLEAN-001
title: Complete user management system
type: feature
priority: high
estimated_hours: 20
---

# PAR-CLEAN-001: Complete user management system

## Problem Statement

The application lacks a complete user management system. We need full CRUD operations for users, a frontend UI, and proper database schema.

## Requirements

### Functional Requirements

**Backend API (FR-1 to FR-5):**

- **FR-1:** User CRUD API endpoints
  - POST /api/users - Create user
  - GET /api/users - List users (paginated)
  - GET /api/users/:id - Get user by ID
  - PUT /api/users/:id - Update user
  - DELETE /api/users/:id - Delete user

- **FR-2:** User authentication endpoints
  - POST /api/auth/login - User login
  - POST /api/auth/logout - User logout
  - POST /api/auth/refresh - Refresh token

- **FR-3:** User service layer
  - Business logic for user operations
  - Password hashing (bcrypt)
  - Input validation
  - Error handling

- **FR-4:** User data models
  - User model with fields: id, email, name, password_hash, created_at
  - Type definitions
  - Serialization methods

**Frontend UI (FR-5 to FR-8):**

- **FR-5:** User list component
  - Display paginated user list
  - Search and filtering
  - Sort by columns
  - Actions: Edit, Delete

- **FR-6:** User form component
  - Create/Edit user form
  - Form validation
  - Error display
  - Submit handling

- **FR-7:** User profile component
  - Display user details
  - Edit profile
  - Change password

- **FR-8:** API client
  - Fetch wrapper for user endpoints
  - Error handling
  - Type-safe responses

**Database (FR-9 to FR-10):**

- **FR-9:** User table migration
  - Create users table
  - Columns: id (UUID), email, name, password_hash, created_at, updated_at
  - Indexes: email (unique), created_at

- **FR-10:** Seed data
  - Test users for development
  - Password: "password123" (hashed)

### Non-Functional Requirements

- **NFR-1:** API response time <200ms
- **NFR-2:** Frontend renders in <1s
- **NFR-3:** Database queries optimized with indexes
- **NFR-4:** 80%+ test coverage

## Acceptance Criteria

- [x] All backend API endpoints implemented
- [x] All frontend components created
- [x] Database migrations applied
- [x] Unit tests passing
- [x] Integration tests passing
- [x] No linting errors
- [x] Type checking passes

## Technical Stack

- Backend: Python 3.11, Flask, SQLAlchemy
- Frontend: React 18, TypeScript, Tailwind CSS
- Database: PostgreSQL 15
- Testing: pytest (backend), Jest (frontend)
```

---

**File:** `.tasks/backlog/PAR-CLEAN-001/file-tasks.md`

```markdown
# File Tasks: PAR-CLEAN-001

## Summary

Total files: 14
- To create: 14
- To modify: 0
- Domains: 3 (backend, frontend, database)

## Files to Create

### Backend Domain (5 files)

#### 1. src/backend/api/users.py (100 lines)
- User API endpoints (CRUD)
- Route handlers: create, list, get, update, delete
- Request validation
- Response serialization

#### 2. src/backend/api/auth.py (80 lines)
- Authentication endpoints
- Login, logout, refresh token
- JWT token generation
- Session management

#### 3. src/backend/models/user.py (60 lines)
- User data model
- SQLAlchemy ORM model
- Field definitions
- Serialization methods (to_dict)

#### 4. src/backend/services/user_service.py (90 lines)
- User business logic
- CRUD operations
- Password hashing (bcrypt)
- Validation logic

#### 5. src/backend/utils/password_hash.py (40 lines)
- Password hashing utilities
- hash_password() function
- verify_password() function
- Uses bcrypt

---

### Frontend Domain (6 files)

#### 1. src/frontend/components/UserList.tsx (120 lines)
- User list component
- Table display with pagination
- Search and filter controls
- Sort functionality
- Edit/Delete actions

#### 2. src/frontend/components/UserForm.tsx (100 lines)
- User create/edit form
- Form validation (react-hook-form)
- Error display
- Submit handling
- Password fields (create only)

#### 3. src/frontend/components/UserProfile.tsx (80 lines)
- User profile display
- Profile editing mode
- Password change form
- Avatar placeholder

#### 4. src/frontend/api/userClient.ts (70 lines)
- API client for user endpoints
- Fetch wrapper functions
- TypeScript types
- Error handling

#### 5. src/frontend/hooks/useUsers.ts (60 lines)
- Custom React hook
- User state management
- CRUD operations
- Loading/error states

#### 6. src/frontend/pages/UsersPage.tsx (90 lines)
- User management page
- Combines UserList + UserForm
- Routing
- Layout

---

### Database Domain (3 files)

#### 1. src/migrations/001_create_users_table.sql (30 lines)
- CREATE TABLE users
- Columns: id, email, name, password_hash, created_at, updated_at
- Primary key: id
- Constraints: email unique, not null

#### 2. src/migrations/002_add_user_indexes.sql (20 lines)
- CREATE INDEX on email (unique)
- CREATE INDEX on created_at
- Performance optimization

#### 3. src/database/seeds/users.sql (40 lines)
- INSERT test users
- 5 sample users
- Hashed passwords
- Development data only

---

## Domain Analysis

### backend
Files: 5
- src/backend/api/users.py
- src/backend/api/auth.py
- src/backend/models/user.py
- src/backend/services/user_service.py
- src/backend/utils/password_hash.py

**No overlap with other domains**

### frontend
Files: 6
- src/frontend/components/UserList.tsx
- src/frontend/components/UserForm.tsx
- src/frontend/components/UserProfile.tsx
- src/frontend/api/userClient.ts
- src/frontend/hooks/useUsers.ts
- src/frontend/pages/UsersPage.tsx

**No overlap with other domains**

### database
Files: 3
- src/migrations/001_create_users_table.sql
- src/migrations/002_add_user_indexes.sql
- src/database/seeds/users.sql

**No overlap with other domains**

---

## Parallel Execution Suitability

✅ **14 files** (exceeds 8 file minimum)
✅ **3 domains** (exceeds 2 domain minimum)
✅ **No file overlaps** (clean domain separation)
✅ **Clear dependencies** (database → backend → frontend)

**Expected:** Parallel execution mode
```

---

**File:** `.tasks/backlog/PAR-CLEAN-001/architecture.md`

```markdown
# Architecture: PAR-CLEAN-001

## System Architecture

```
Frontend (React)
    │
    ├─► UserList Component
    ├─► UserForm Component
    ├─► UserProfile Component
    │
    └─► API Client (userClient.ts)
            │
            ▼
Backend API (Flask)
    │
    ├─► /api/users (users.py)
    ├─► /api/auth (auth.py)
    │
    └─► UserService (user_service.py)
            │
            ├─► User Model (user.py)
            │
            └─► Database (PostgreSQL)
                    │
                    ├─► users table
                    └─► indexes
```

## Domain Breakdown

### Database Domain
**Responsibility:** Data persistence layer

**Components:**
- users table (migration 001)
- email index (migration 002)
- created_at index (migration 002)
- seed data (users.sql)

**Dependencies:** None

**Execution Order:** First (provides schema for backend)

---

### Backend Domain
**Responsibility:** API and business logic

**Components:**
- API endpoints (users.py, auth.py)
- Service layer (user_service.py)
- Data models (user.py)
- Utilities (password_hash.py)

**Dependencies:**
- Requires: Database schema (from database domain)

**Execution Order:** Second (provides API for frontend)

---

### Frontend Domain
**Responsibility:** User interface

**Components:**
- Components (UserList, UserForm, UserProfile)
- API client (userClient.ts)
- Hooks (useUsers.ts)
- Pages (UsersPage.tsx)

**Dependencies:**
- Requires: Backend API (from backend domain)

**Execution Order:** Third (consumes backend API)

---

## Dependency Graph

```
database domain (no deps)
    │
    ▼
backend domain (depends on database)
    │
    ▼
frontend domain (depends on backend)
```

**Merge Order:** database → backend → frontend

---

## File Isolation

### No Shared Files

All files are domain-specific:
- Backend files in `src/backend/`
- Frontend files in `src/frontend/`
- Database files in `src/migrations/` and `src/database/`

**No file conflicts expected during parallel execution**

---

## Performance Expectations

### Sequential Execution
- Database: 10 minutes
- Backend: 15 minutes
- Frontend: 20 minutes
- **Total: 45 minutes**

### Parallel Execution
- All domains: max(10, 15, 20) = 20 minutes
- Merge: 1 minute
- Validation: 5 minutes
- **Total: 26 minutes**

**Speedup: 1.7x** (45min → 26min)

---

## Risk Analysis

### Low Risk
- ✅ No file overlaps
- ✅ Clear domain boundaries
- ✅ Well-defined dependencies

### Medium Risk
- ⚠️ Frontend depends on backend API shape (types must match)
- ⚠️ Backend depends on database schema (column names must match)

**Mitigation:** Use TypeScript types and SQLAlchemy models for consistency

### High Risk
- None identified

---

## Rollback Plan

If parallel execution fails:
1. Clean up worktrees
2. Fallback to sequential mode
3. Execute domains in dependency order

If merge conflicts occur:
1. Abort merge
2. Manual resolution required (unlikely given no file overlaps)
```

---

### Expected Parallel Detection Output

```json
{
  "viable": true,
  "reason": "14 files across 3 domains (meets all thresholds)",
  "execution_mode": "parallel",
  "file_count": 14,
  "domain_count": 3,
  "domains": {
    "backend": [
      "src/backend/api/users.py",
      "src/backend/api/auth.py",
      "src/backend/models/user.py",
      "src/backend/services/user_service.py",
      "src/backend/utils/password_hash.py"
    ],
    "frontend": [
      "src/frontend/components/UserList.tsx",
      "src/frontend/components/UserForm.tsx",
      "src/frontend/components/UserProfile.tsx",
      "src/frontend/api/userClient.ts",
      "src/frontend/hooks/useUsers.ts",
      "src/frontend/pages/UsersPage.tsx"
    ],
    "database": [
      "src/migrations/001_create_users_table.sql",
      "src/migrations/002_add_user_indexes.sql",
      "src/database/seeds/users.sql"
    ]
  },
  "parallel_plan": {
    "backend": {
      "files": [
        "src/backend/api/users.py",
        "src/backend/api/auth.py",
        "src/backend/models/user.py",
        "src/backend/services/user_service.py",
        "src/backend/utils/password_hash.py"
      ],
      "task_description": "Implement backend API endpoints, services, and models for user management. Create user CRUD endpoints, authentication endpoints, user service layer with business logic, user data model, and password hashing utilities.",
      "estimated_complexity": "medium",
      "file_count": 5
    },
    "frontend": {
      "files": [
        "src/frontend/components/UserList.tsx",
        "src/frontend/components/UserForm.tsx",
        "src/frontend/components/UserProfile.tsx",
        "src/frontend/api/userClient.ts",
        "src/frontend/hooks/useUsers.ts",
        "src/frontend/pages/UsersPage.tsx"
      ],
      "task_description": "Create frontend UI components and API client for user management. Implement user list with pagination and filtering, user creation/editing form, user profile display, API client for backend endpoints, custom React hooks for state management, and user management page layout.",
      "estimated_complexity": "medium",
      "file_count": 6
    },
    "database": {
      "files": [
        "src/migrations/001_create_users_table.sql",
        "src/migrations/002_add_user_indexes.sql",
        "src/database/seeds/users.sql"
      ],
      "task_description": "Add database migrations and seed data for users table. Create users table with proper schema, add indexes for performance optimization, and insert test user data for development.",
      "estimated_complexity": "low",
      "file_count": 3
    }
  },
  "thresholds": {
    "min_files": 8,
    "min_domains": 2
  },
  "metadata": {
    "epic_id": "PAR-CLEAN-001",
    "epic_title": "Complete user management system",
    "analysis_timestamp": "2025-10-19T10:45:00Z"
  },
  "recommendations": {
    "merge_order": ["database", "backend", "frontend"],
    "estimated_speedup": "1.7x",
    "conflict_risk": "low"
  }
}
```

---

### Validation Commands

```bash
# 1. Run parallel detection
python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  --epic-dir .tasks/backlog/PAR-CLEAN-001 \
  --output .workflow/outputs/PAR-CLEAN-001/parallel_analysis.json

# 2. Verify parallel mode
MODE=$(jq -r '.execution_mode' .workflow/outputs/PAR-CLEAN-001/parallel_analysis.json)
test "$MODE" = "parallel" && echo "✅ Parallel mode" || echo "❌ Expected parallel"

# 3. Verify file count
COUNT=$(jq -r '.file_count' .workflow/outputs/PAR-CLEAN-001/parallel_analysis.json)
test "$COUNT" -eq 14 && echo "✅ 14 files" || echo "❌ Expected 14 files"

# 4. Verify domain count
DOMAINS=$(jq -r '.domain_count' .workflow/outputs/PAR-CLEAN-001/parallel_analysis.json)
test "$DOMAINS" -eq 3 && echo "✅ 3 domains" || echo "❌ Expected 3 domains"

# 5. List domains
echo "Domains detected:"
jq -r '.domains | keys[]' .workflow/outputs/PAR-CLEAN-001/parallel_analysis.json

# 6. Check parallel plan exists
jq '.parallel_plan | keys' .workflow/outputs/PAR-CLEAN-001/parallel_analysis.json
```

---

### Expected Workflow Execution Trace

```
=================================================================
Tier 1 Workflow: PAR-CLEAN-001
=================================================================

Phase 0: Preflight
----------------------------------------------------------------------
✅ Epic directory found: .tasks/backlog/PAR-CLEAN-001
✅ Required files present: spec.md, file-tasks.md, architecture.md
✅ Git status clean

Running parallel detection...
  File count: 14
  Domain count: 3
  Domains: backend, frontend, database
  Viable for parallel: true
  Reason: 14 files across 3 domains (meets all thresholds)

Execution mode: PARALLEL
Output: .workflow/outputs/PAR-CLEAN-001/parallel_analysis.json

🔀 Phase 1B: Parallel Implementation
======================================================================

Parallel execution across domains:
  - backend: 5 files
    Task: Implement backend API endpoints, services, and models...
  - frontend: 6 files
    Task: Create frontend UI components and API client...
  - database: 3 files
    Task: Add database migrations and seed data...

Creating isolated worktrees...
----------------------------------------------------------------------
  Creating worktree for: backend
    ✅ Created: .worktrees/PAR-CLEAN-001-backend-a3f2b1c4
    Branch: feature/PAR-CLEAN-001/backend
  Creating worktree for: frontend
    ✅ Created: .worktrees/PAR-CLEAN-001-frontend-d5e6f7g8
    Branch: feature/PAR-CLEAN-001/frontend
  Creating worktree for: database
    ✅ Created: .worktrees/PAR-CLEAN-001-database-h9i0j1k2
    Branch: feature/PAR-CLEAN-001/database

✅ All worktrees created successfully

Deploying parallel agents...
----------------------------------------------------------------------

⚠️  IMPORTANT: Agents will work in parallel. Do not interrupt.

⏳ Waiting for all agents to complete...
----------------------------------------------------------------------

Agents are working in parallel:
  - backend: .worktrees/PAR-CLEAN-001-backend-a3f2b1c4
  - frontend: .worktrees/PAR-CLEAN-001-frontend-d5e6f7g8
  - database: .worktrees/PAR-CLEAN-001-database-h9i0j1k2

[Agents execute in parallel...]
[Duration: ~20 minutes]

📊 Collecting results from parallel agents...
----------------------------------------------------------------------

Domain: backend
  Status: success
  Files created: 5
  Files modified: 0
  ✅ Results copied to main repo

Domain: frontend
  Status: success
  Files created: 6
  Files modified: 0
  ✅ Results copied to main repo

Domain: database
  Status: success
  Files created: 3
  Files modified: 0
  ✅ Results copied to main repo

======================================================================
Parallel Execution Summary:
  Total domains: 3
  Success: 3
  Partial: 0
  Failed: 0
======================================================================

✅ Phase 1B Complete: Parallel Implementation

🔗 Phase 1C: Sequential Merge
======================================================================

✅ All domain implementations succeeded - proceeding with merge

Merge order (dependency-based):
  1. database
  2. backend
  3. frontend

Merging: database
  Branch: feature/PAR-CLEAN-001/database
  Merging into: main
  ✅ Merged successfully

Merging: backend
  Branch: feature/PAR-CLEAN-001/backend
  Merging into: main
  ✅ Merged successfully

Merging: frontend
  Branch: feature/PAR-CLEAN-001/frontend
  Merging into: main
  ✅ Merged successfully

✅ All merges completed successfully
✅ Working directory clean after merge

🧹 Cleaning up worktrees...
  Removing: backend (PAR-CLEAN-001-backend-a3f2b1c4)
    ✅ Removed
  Removing: frontend (PAR-CLEAN-001-frontend-d5e6f7g8)
    ✅ Removed
  Removing: database (PAR-CLEAN-001-database-h9i0j1k2)
    ✅ Removed

✅ Worktree cleanup complete
✅ Phase 1C Complete: Sequential Merge

Phase 2: Validation
----------------------------------------------------------------------
Running linter... ✅ No errors
Running type checker... ✅ No errors
Running tests... ✅ All passed (45/45)

Phase 5: Commit & Cleanup
----------------------------------------------------------------------
Creating commit...
✅ Commit: def5678 "feat: Complete user management system (PAR-CLEAN-001)"

Moving epic to completed...
✅ Moved: .tasks/backlog/PAR-CLEAN-001 → .tasks/completed/PAR-CLEAN-001

=================================================================
✅ Workflow Complete: PAR-CLEAN-001
=================================================================
Duration: 26m 30s
Mode: Parallel (3 domains)
Files changed: 14
Speedup: 1.7x (vs 45min sequential)
Status: Success
```

---

## Summary

This document provides complete, runnable examples for:

- ✅ **Example 1:** Sequential execution (2 files, 1 domain)
- ✅ **Example 2:** Parallel execution with clean merge (14 files, 3 domains)

Each example includes:
- ✅ Complete epic specification files (spec.md, file-tasks.md, architecture.md)
- ✅ Full implementation code (Python, TypeScript, SQL)
- ✅ Expected parallel detection output (JSON)
- ✅ Validation commands (bash)
- ✅ Expected workflow execution trace

**Additional Examples (Summary Only):**

- **Example 3:** Parallel with conflicts (intentional overlapping files)
- **Example 4:** Validation failure (lint errors, retry loop)
- **Example 5:** GitHub integration (epic + sub-issues)

See `WORKFLOW_TESTING_GUIDE.md` for complete details on Examples 3-5.

---

**Generated:** 2025-10-19
**Author:** Claude Code (Tier 1 Workflow Testing Examples)
**Version:** 1.0
