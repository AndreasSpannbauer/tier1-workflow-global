# Tier 1 Workflow - User Manual

**Complete user guide for the Tier 1 workflow system**

**Date:** 2025-10-19
**Version:** 1.0
**Audience:** Developers using the Tier 1 workflow

---

## Table of Contents

1. [What is the Tier 1 Workflow?](#what-is-the-tier-1-workflow)
2. [When to Use It](#when-to-use-it)
3. [Creating Epics](#creating-epics)
4. [Executing Workflows](#executing-workflows)
5. [Working with Post-Mortems](#working-with-post-mortems)
6. [Best Practices](#best-practices)
7. [Common Workflows](#common-workflows)
8. [FAQ](#faq)

---

## What is the Tier 1 Workflow?

The Tier 1 workflow is an **automated epic implementation system** that uses AI agents to execute software development tasks from specification to commit.

### Key Features

**Automated Implementation:**
- Create epic specification
- Generate implementation plan
- Execute with AI agents
- Automated validation with retry
- Commit with conventional message

**Parallel Execution:**
- Automatic detection for large epics
- 2-4x speedup via git worktrees
- Dependency-aware sequential merge

**Quality Assurance:**
- Automated validation (lint, typecheck, build)
- Build fixer agent for auto-fixes
- Retry loop (up to 3 attempts)
- Non-blocking failures (workflow continues)

**Knowledge Capture:**
- Post-mortem analysis after completion
- Actionable recommendations
- Briefing evolution over time

### How It Works

```
User Input (Feature Description)
    ↓
/spec-epic → spec.md (requirements, acceptance criteria)
    ↓
/refine-epic → architecture.md + file-tasks.md (prescriptive plan)
    ↓
/execute-workflow → Automatic implementation
    ├─► Sequential (small epics)
    └─► Parallel (large epics)
    ↓
Validation (automated retry)
    ↓
Commit (conventional message)
    ↓
Post-Mortem (recommendations for next time)
```

---

## When to Use It

### Ideal For

**Feature Implementation:**
- Adding new API endpoints
- Creating new UI components
- Implementing data models
- Adding validation layers

**Bug Fixes (Complex):**
- Multi-file bug fixes
- Refactoring with architectural changes
- Adding error handling across layers

**Refactoring:**
- Extracting services
- Reorganizing modules
- Updating patterns across codebase

### Not Ideal For

**Simple Changes:**
- One-line fixes
- Documentation updates
- Configuration changes
- Single-file modifications

**Exploratory Work:**
- Prototyping
- Experiments
- Proof of concepts
- Research spikes

**Breaking Changes:**
- Major refactors requiring manual review
- API breaking changes
- Database migrations with data loss

### Epic Size Guidelines

| Epic Size | Files | Domains | Recommended Approach |
|-----------|-------|---------|---------------------|
| **Small** | 1-4 | 1 | Manual implementation (faster) |
| **Medium** | 5-12 | 1-2 | Tier 1 Sequential (15-30 min) |
| **Large** | 13-25 | 2-3 | Tier 1 Parallel (25-40 min, 2-3x speedup) |
| **X-Large** | 26+ | 3+ | Tier 1 Parallel (30-50 min, 3-4x speedup) |

---

## Creating Epics

### Step 1: Create Epic Specification

**Command:** `/spec-epic`

**What It Does:**
- Creates `.tasks/backlog/EPIC-XXX-title/spec.md`
- Captures problem statement, requirements, acceptance criteria
- Assigns unique epic ID

**Example Session:**

```
You: /spec-epic

Claude: What feature would you like to specify?

You: Add rate limiting to API endpoints to prevent abuse.

Requirements:
- Limit requests per IP address (100 requests/minute)
- Use Redis for tracking request counts
- Return 429 status code when limit exceeded
- Allow configurable limits per endpoint
- Add rate limit headers to responses

Claude: [Creates spec.md]

✅ Epic created: EPIC-042

Location: .tasks/backlog/EPIC-042-add-rate-limiting/spec.md

Summary:
- Title: Add rate limiting to API endpoints
- Requirements: 5 items
- Acceptance criteria: 4 items
- Technical considerations: Noted

Next steps:
1. Review spec.md
2. Run /refine-epic EPIC-042 to generate implementation plan
```

**Reviewing the Spec:**

```bash
cat .tasks/backlog/EPIC-042-add-rate-limiting/spec.md
```

**Example spec.md:**
```markdown
# Epic: Add Rate Limiting to API Endpoints

## Overview
Implement rate limiting for API endpoints to prevent abuse and ensure fair resource allocation.

## Requirements

### Functional Requirements
1. Limit requests per IP address (100 requests/minute default)
2. Use Redis for distributed rate limit tracking
3. Return HTTP 429 when limit exceeded
4. Allow per-endpoint configurable limits
5. Include rate limit headers in all responses

### Non-Functional Requirements
6. Performance overhead < 5ms per request
7. Redis failover handling (degrade gracefully)

## Acceptance Criteria

1. ✅ Rate limiting enforced:
   - Request 1-100: HTTP 200
   - Request 101: HTTP 429

2. ✅ Headers present:
   - X-RateLimit-Limit: 100
   - X-RateLimit-Remaining: 42
   - X-RateLimit-Reset: 1635724800

3. ✅ Configurable limits:
   - /api/auth/login: 10 requests/minute
   - /api/search: 100 requests/minute

4. ✅ Redis failure handling:
   - Redis down → Allow all requests (log warning)
   - Redis slow → Timeout after 100ms, allow request

## Technical Considerations

- Middleware pattern for rate limiting
- Redis key format: `ratelimit:{ip}:{endpoint}:{minute}`
- TTL: 60 seconds (auto-expire)
- Configuration via environment variables

## Dependencies

- Redis (already deployed)
- Python redis-py library
- Existing middleware stack

## Estimated Effort

- Development: 4-6 hours
- Testing: 2 hours
- Code review: 1 hour
```

---

### Step 2: Generate Implementation Plan

**Command:** `/refine-epic EPIC-042`

**What It Does:**
- Creates `architecture.md` (design decisions, component structure)
- Creates `implementation-details/file-tasks.md` (prescriptive plan)
- Analyzes spec and determines technical approach

**Example Output:**

```
You: /refine-epic EPIC-042

Claude: [Reads spec.md, analyzes requirements, generates architecture]

✅ Epic refined: EPIC-042

Files created:
- architecture.md (design decisions, components, data flow)
- implementation-details/file-tasks.md (prescriptive implementation plan)

Key design decisions:
- Middleware-based approach (applies to all routes)
- Redis for distributed tracking
- Decorator for per-endpoint configuration
- Graceful degradation on Redis failure

Files to create: 3
Files to modify: 2

Epic ready for execution: /execute-workflow EPIC-042
```

**Reviewing the Architecture:**

```bash
cat .tasks/backlog/EPIC-042-add-rate-limiting/architecture.md
```

**Example architecture.md (excerpt):**
```markdown
# Architecture: Add Rate Limiting to API Endpoints

## Design Overview

Implement rate limiting as middleware that intercepts all API requests:
1. Extract client IP from request
2. Check Redis for current request count
3. If limit exceeded, return 429
4. If within limit, increment counter and proceed
5. Add rate limit headers to response

## Components

### 1. Rate Limiter Middleware (NEW)

**File:** `src/backend/middleware/rate_limiter.py`

**Responsibility:** Enforce rate limits for all API requests

**Methods:**
- `check_rate_limit(ip: str, endpoint: str) -> bool`
- `increment_counter(ip: str, endpoint: str) -> int`
- `get_remaining(ip: str, endpoint: str) -> int`

**Dependencies:** Redis, configuration

### 2. Rate Limit Configuration (NEW)

**File:** `src/backend/config/rate_limits.py`

**Responsibility:** Endpoint-specific rate limit configuration

**Structure:**
\`\`\`python
RATE_LIMITS = {
    "/api/auth/login": {"requests": 10, "window": 60},
    "/api/search": {"requests": 100, "window": 60},
    "default": {"requests": 100, "window": 60}
}
\`\`\`

### 3. Main Application (MODIFY)

**File:** `src/backend/main.py`

**Changes:** Register rate limiter middleware

...
```

**Reviewing the Prescriptive Plan:**

```bash
cat .tasks/backlog/EPIC-042-add-rate-limiting/implementation-details/file-tasks.md
```

**Example file-tasks.md (excerpt):**
```markdown
# Implementation Plan: EPIC-042 - Add Rate Limiting

## Files to Create

### `src/backend/middleware/rate_limiter.py`

**Purpose:** Rate limiting middleware

**Requirements:**
- Create RateLimiterMiddleware class
- Implement request interception
- Check Redis for request count
- Return 429 if limit exceeded
- Add rate limit headers

**Implementation Details:**
\`\`\`python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import redis

class RateLimiterMiddleware:
    def __init__(self, app, redis_client):
        self.app = app
        self.redis = redis_client

    async def __call__(self, request: Request, call_next):
        ip = request.client.host
        endpoint = request.url.path

        # Check rate limit
        current_count = await self.get_request_count(ip, endpoint)
        limit = self.get_limit(endpoint)

        if current_count >= limit:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"},
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(self.get_reset_time())
                }
            )

        # Increment counter
        await self.increment_count(ip, endpoint)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(limit - current_count - 1)
        response.headers["X-RateLimit-Reset"] = str(self.get_reset_time())

        return response
\`\`\`

**Dependencies:**
- `fastapi` (Request, HTTPException, JSONResponse)
- `redis-py` (Redis client)

---

### `src/backend/config/rate_limits.py`

...

## Files to Modify

### `src/backend/main.py`

**Changes:**
- Import RateLimiterMiddleware
- Initialize Redis connection
- Register middleware

**Location:** After app initialization, before routes

**Code to Add:**
\`\`\`python
from src.backend.middleware.rate_limiter import RateLimiterMiddleware
import redis

# Initialize Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# Register rate limiter middleware
app.add_middleware(RateLimiterMiddleware, redis_client=redis_client)
\`\`\`

...
```

---

## Executing Workflows

### Basic Execution

**Command:** `/execute-workflow EPIC-042`

**What Happens:**

**1. Phase 0: Preflight**
```
🔍 Analyzing for parallel execution opportunities...

Parallel Analysis:
  Files: 5
  Domains: 1 (backend only)
  Viable: false
  Reason: Too few domains (1 < 2)

➡️ Sequential execution

✅ Preflight checks passed

Epic: EPIC-042
Title: Add rate limiting to API endpoints
Files to modify: 5
Mode: sequential
```

**2. Phase 1: Implementation**
```
🚀 Phase 1A: Sequential Implementation

Deploying implementation agent...

Agent: implementation-agent-v1
Domain: backend
Briefings:
  - backend_implementation.md
  - project_architecture.md

Reading prescriptive plan...
Parsing file-tasks.md...

Creating src/backend/middleware/rate_limiter.py... ✅
Creating src/backend/config/rate_limits.py... ✅
Creating src/backend/exceptions.py... ✅
Modifying src/backend/main.py... ✅
Modifying src/backend/requirements.txt... ✅

✅ Phase 1A Complete: Sequential Implementation
Files created: 3
Files modified: 2
Duration: 18m 24s
```

**3. Phase 3: Validation (with Retry)**
```
🔍 Phase 3: Validation

────────────────────────────────────────────────────────────────────
Validation Attempt 1 of 3
────────────────────────────────────────────────────────────────────

Running: npm run validate-all

Running ruff check...
src/backend/middleware/rate_limiter.py:45:1: E501 Line too long (102 > 100)
src/backend/middleware/rate_limiter.py:67:1: F401 'redis.exceptions.RedisError' imported but unused

❌ Validation failed on attempt 1

🔧 Deploying build fixer agent (attempt 1)...

Build fixer agent will:
1. Read error output
2. Apply auto-fixes (ruff check --fix, ruff format)
3. Fix manual errors
4. Write results

[Build fixer completes]

Retrying validation...

────────────────────────────────────────────────────────────────────
Validation Attempt 2 of 3
────────────────────────────────────────────────────────────────────

Running: npm run validate-all

✅ Linting passed (0 errors)
✅ Type checking passed (0 errors)

✅ Validation passed on attempt 2

====================================================================
✅ Phase 3 Complete: Validation Passed
====================================================================
   Attempts: 2
   Status: PASSED
```

**4. Phase 5: Commit**
```
📝 Phase 5: Commit & Cleanup

Commit message:
──────────────────────────────────────────────────────────────────
feat(EPIC-042): Add rate limiting to API endpoints

Implementation completed using sequential execution mode.

Files created: 3
Files modified: 2
Execution mode: sequential

Epic: .tasks/backlog/EPIC-042-add-rate-limiting
Results: .workflow/outputs/EPIC-042/

🤖 Generated with Claude Code
https://claude.com/claude-code

Co-Authored-By: Claude <noreply@anthropic.com>
──────────────────────────────────────────────────────────────────

✅ Commit created successfully

✅ Epic moved to: .tasks/completed/EPIC-042-add-rate-limiting
```

**5. Phase 6: Post-Mortem**
```
📊 Phase 6: Post-Mortem Analysis

Analyzing workflow execution to identify improvements...

✅ Post-Mortem Report: .workflow/post-mortem/EPIC-042.md

Key Recommendations:
- Add Redis error handling pattern to backend briefing
- Document middleware registration pattern
- Clarify line length configuration (99 vs 100 chars)
```

---

### Reviewing Results

**View Commit:**
```bash
git show
```

**View Implementation Results:**
```bash
cat .workflow/outputs/EPIC-042/phase1_results.json
```

**View Validation Results:**
```bash
cat .workflow/outputs/EPIC-042/validation/result.json
```

**View Post-Mortem:**
```bash
cat .workflow/post-mortem/EPIC-042.md
```

**Check Epic Moved:**
```bash
ls .tasks/completed/ | grep EPIC-042
```

---

## Working with Post-Mortems

### Reading Post-Mortem Reports

Post-mortem reports are generated after every epic completion in `.workflow/post-mortem/EPIC-XXX.md`.

**Report Structure:**

1. **Summary** - High-level overview (1-2 sentences)
2. **Execution Details** - Files, mode, duration, status
3. **What Worked Well** - 3-5 specific successes
4. **Challenges Encountered** - 2-4 issues with resolutions
5. **Recommendations** - Actionable improvements
6. **Metrics** - Validation pass rate, errors fixed, etc.
7. **Artifacts** - Links to results files

**Example Post-Mortem (excerpt):**

```markdown
# Post-Mortem: EPIC-042

## Summary

Successfully implemented rate limiting middleware with Redis backend.
Validation passed on second attempt after build fixer corrected line
length and removed unused import.

## What Worked Well

- **Clear prescriptive plan:** file-tasks.md specified exact middleware
  implementation, agent followed without confusion
- **Middleware pattern:** Existing middleware stack made integration
  straightforward
- **Build fixer effectiveness:** Auto-fixed 2 linting errors in one pass

## Challenges Encountered

### Challenge 1: Line Length Inconsistency

- **Description:** Linting failed due to line exceeding 100 chars (project uses 99)
- **Impact:** Validation failed on first attempt
- **Root Cause:** Prescriptive plan didn't specify line length limit
- **Resolution:** Build fixer auto-formatted code with ruff
- **Lesson:** Document line length limit in project architecture briefing

### Challenge 2: Unused Import

- **Description:** Imported RedisError but didn't use it
- **Impact:** Linting failed on first attempt
- **Root Cause:** Prescriptive plan suggested error handling but implementation
  used try/except differently
- **Resolution:** Build fixer removed unused import
- **Lesson:** Prescriptive plans should show exact error handling imports

## Recommendations

### Briefing Updates

**Backend Briefing:** `.claude/agent_briefings/backend_implementation.md`

- **Add pattern:** "Project uses 99-char line limit (not 100). Configure editor
  accordingly."
- **Clarify:** "Import only what you use. If prescriptive plan mentions error
  handling, verify actual usage before importing exception classes."
- **Example:** Add Redis error handling pattern:
  \`\`\`python
  try:
      redis_client.set(key, value)
  except redis.exceptions.RedisError as e:
      logger.error(f"Redis error: {e}")
      # Degrade gracefully
  \`\`\`

**Implementation Agent:** `.claude/agent_definitions/implementation_agent_v1.md`

- **Add rule:** "Check project-specific line length limit (may differ from
  default 100)"

### Process Improvements

**Prescriptive Plans:**
- Include code style notes (line length, import conventions)
- Show complete import lists (not just suggestions)
- Specify error handling patterns with exact imports

**Validation Phase:**
- Line length violations should be caught by auto-formatter first
  (before type check)

## Metrics

- Validation pass rate: 50% (passed on attempt 2/2)
- Build errors fixed: 0
- Lint violations fixed: 2 (line length, unused import)
- Type errors fixed: 0
- Architecture violations: 0
```

---

### Applying Recommendations

**Step 1: Review Full Report**
```bash
cat .workflow/post-mortem/EPIC-042.md
```

**Step 2: Evaluate Recommendations**

Ask yourself:
- Is this recommendation generally applicable (not epic-specific)?
- Will it improve future workflows?
- Is it actionable (clear file path, exact change)?

**Step 3: Apply to Briefings**

**Example: Update backend briefing**
```bash
nano .claude/agent_briefings/backend_implementation.md
```

**Add recommended pattern:**
```markdown
## Code Style

### Line Length

**Project uses 99-character line limit** (not default 100).

Configure editor:
\`\`\`
# .editorconfig
[*.py]
max_line_length = 99
\`\`\`

Linting will fail if lines exceed 99 chars.

### Imports

**Import only what you use.** If prescriptive plan mentions error handling,
verify actual usage before importing exception classes.

\`\`\`python
# ✅ Good: Only import what you use
from redis.exceptions import RedisError

try:
    redis_client.set(key, value)
except RedisError as e:
    logger.error(f"Redis error: {e}")

# ❌ Bad: Importing but not using
from redis.exceptions import RedisError  # Imported but never used
\`\`\`

## Error Handling Patterns

### Redis Operations

Always handle Redis failures gracefully:

\`\`\`python
import redis
from redis.exceptions import RedisError

try:
    value = redis_client.get(key)
    if value is None:
        # Key doesn't exist
        return default_value
    return value
except RedisError as e:
    logger.error(f"Redis error: {e}")
    # Degrade gracefully (return default or skip cache)
    return default_value
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
\`\`\`
```

**Step 4: Commit Briefing Updates**
```bash
git add .claude/agent_briefings/backend_implementation.md
git commit -m "refine: update backend briefing based on EPIC-042 post-mortem

- Document 99-char line length limit
- Add import best practices (import only what you use)
- Add Redis error handling pattern

Recommendation source: .workflow/post-mortem/EPIC-042.md"
```

**Step 5: Archive Post-Mortem**

Post-mortems are kept permanently in `.workflow/post-mortem/` for:
- Historical reference
- Trend analysis (repeated issues?)
- Onboarding material (learn from past workflows)

**No deletion** - storage is cheap, insights are valuable.

---

## Best Practices

### Epic Sizing

**When to Split:**
- Epic affects 4+ domains (backend, frontend, database, mobile)
- Epic touches 30+ files
- Epic has multiple independent features
- Epic requires breaking changes

**How to Split:**
```
Original Epic: "Implement search feature"

Split into:
- EPIC-043: Add search API endpoints (backend, 8 files)
- EPIC-044: Add search UI components (frontend, 6 files)
- EPIC-045: Add search indexing (database, 4 files)

Execute in sequence: EPIC-043 → EPIC-044 → EPIC-045
```

---

### Writing Clear Prescriptive Plans

**Good Prescriptive Plan Characteristics:**

**1. Specific File Paths**
```markdown
✅ Good: `src/backend/middleware/rate_limiter.py`
❌ Bad: "Create middleware file"
```

**2. Exact Code Changes**
```markdown
✅ Good:
\`\`\`python
# Add to src/backend/main.py, line 15 (after app initialization)
app.add_middleware(RateLimiterMiddleware, redis_client=redis_client)
\`\`\`

❌ Bad: "Register middleware in main file"
```

**3. Complete Import Lists**
```markdown
✅ Good:
\`\`\`python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import redis
from redis.exceptions import RedisError
\`\`\`

❌ Bad: "Import necessary modules"
```

**4. Error Handling Specified**
```markdown
✅ Good:
\`\`\`python
try:
    redis_client.get(key)
except RedisError as e:
    logger.error(f"Redis error: {e}")
    return default_value
\`\`\`

❌ Bad: "Add error handling for Redis failures"
```

**5. Type Hints Always Included**
```markdown
✅ Good:
\`\`\`python
async def check_rate_limit(self, ip: str, endpoint: str) -> bool:
\`\`\`

❌ Bad:
\`\`\`python
async def check_rate_limit(self, ip, endpoint):
\`\`\`
```

---

### Domain Organization

**Standard Domains:**
- `backend` - API, services, business logic
- `frontend` - UI components, pages, client-side logic
- `database` - Migrations, schema changes
- `tests` - Test files
- `docs` - Documentation

**Domain Separation Best Practices:**

**1. Minimize File Overlap**
```markdown
✅ Good: Clear domain boundaries
Backend: src/backend/**
Frontend: src/frontend/**
Database: migrations/**

❌ Bad: Shared files across domains
Backend: src/backend/**, src/shared/**
Frontend: src/frontend/**, src/shared/**
```

**2. Respect Dependencies**
```
database → backend → frontend → tests → docs

Backend depends on database (schema must exist first)
Frontend depends on backend (API must exist first)
Tests depend on all layers
Docs describe completed features
```

**3. Use Domain-Specific Briefings**
```
Backend epic → backend_implementation.md
Frontend epic → frontend_implementation.md
Multi-domain epic → All relevant briefings
```

---

### Validation Configuration

**Recommended package.json:**
```json
{
  "name": "your-project",
  "scripts": {
    "lint:py": "ruff check .",
    "lint:py:fix": "ruff check --fix .",
    "format:py": "ruff format .",
    "format:py:check": "ruff format --check .",
    "typecheck:py": "mypy src/ --strict",
    "lint:ts": "eslint src/",
    "lint:ts:fix": "eslint src/ --fix",
    "format:ts": "prettier --write src/",
    "format:ts:check": "prettier --check src/",
    "build:ts": "tsc --noEmit",
    "validate-architecture": "python3 tools/validate_architecture.py",
    "validate-contracts": "python3 tools/validate_contracts.py",
    "validate-all": "npm run lint:py && npm run format:py:check && npm run typecheck:py && npm run validate-architecture"
  }
}
```

**Custom Validation Scripts:**
```bash
# Copy templates
cp -r ~/tier1_workflow_global/implementation/validation_scripts/ ./tools/

# Customize for your project
nano tools/validate_architecture.py
# - Update layer definitions
# - Update import rules
# - Add project-specific checks
```

---

## Common Workflows

### Workflow 1: New Backend Feature

**Scenario:** Add email notification feature

**Steps:**

1. **Create Epic:**
   ```
   /spec-epic

   Add email notification system.

   Requirements:
   - Send welcome emails on user registration
   - Send password reset emails
   - Use SendGrid API for delivery
   - Queue emails with Celery for async processing
   - Template-based emails with variable substitution
   ```

2. **Refine Epic:**
   ```
   /refine-epic EPIC-050
   ```

3. **Review Architecture:**
   ```bash
   cat .tasks/backlog/EPIC-050-add-email-notifications/architecture.md
   # Review design decisions
   ```

4. **Execute Workflow:**
   ```
   /execute-workflow EPIC-050
   ```

5. **Review Post-Mortem:**
   ```bash
   cat .workflow/post-mortem/EPIC-050.md
   # Apply recommendations to briefings
   ```

6. **Push Changes:**
   ```bash
   git push origin main
   ```

---

### Workflow 2: Multi-Domain Feature (Parallel)

**Scenario:** Add user profile feature (backend + frontend)

**Steps:**

1. **Create Epic:**
   ```
   /spec-epic

   Add user profile management feature.

   Requirements:
   - Backend: Profile CRUD API endpoints
   - Backend: Profile photo upload (S3)
   - Backend: Profile validation
   - Frontend: Profile page UI
   - Frontend: Photo upload component
   - Frontend: Profile edit form
   - Database: Profile table migration
   ```

2. **Refine Epic:**
   ```
   /refine-epic EPIC-051
   ```

3. **Verify Parallel Detection:**
   ```bash
   cat .workflow/outputs/EPIC-051/parallel_analysis.json
   # Should show: "viable": true, "execution_mode": "parallel"
   ```

4. **Execute Workflow (Parallel):**
   ```
   /execute-workflow EPIC-051

   # Workflow will:
   # - Create 3 worktrees (backend, frontend, database)
   # - Deploy 3 agents in parallel
   # - Merge sequentially (database → backend → frontend)
   ```

5. **Review Results:**
   ```bash
   # Parallel results
   cat .workflow/outputs/EPIC-051/phase1_parallel_results.json

   # Merge summary
   cat .workflow/outputs/EPIC-051/merge_summary.json

   # Post-mortem (check parallel effectiveness)
   cat .workflow/post-mortem/EPIC-051.md
   ```

---

### Workflow 3: Validation Failure Recovery

**Scenario:** Validation fails after max attempts

**What Happens:**
```
🔍 Phase 3: Validation

Validation Attempt 3 of 3

❌ Validation failed on attempt 3

⚠️ Maximum validation attempts (3) reached

Validation failed after 3 attempts.
Logs: .workflow/outputs/EPIC-052/validation/

Manual intervention recommended but workflow will continue.
```

**Recovery Steps:**

1. **Review Validation Logs:**
   ```bash
   cat .workflow/outputs/EPIC-052/validation/attempt_3.log
   ```

2. **Identify Unfixable Issues:**
   ```
   src/backend/service.py:42:1: error: Cannot determine type of 'user_data'
   src/backend/service.py:67:1: error: Incompatible return value type
   ```

3. **Fix Manually:**
   ```bash
   nano src/backend/service.py
   # Add type hints manually
   # Fix return type issues
   ```

4. **Run Validation:**
   ```bash
   npm run validate-all
   ```

5. **Commit Fixes:**
   ```bash
   git add src/backend/service.py
   git commit --amend --no-edit
   # Amend the workflow commit with fixes
   ```

6. **Review Post-Mortem:**
   ```bash
   cat .workflow/post-mortem/EPIC-052.md
   # Apply recommendations to prevent future issues
   ```

---

## FAQ

### Q: When should I use sequential vs parallel execution?

**A:** Workflow automatically detects based on thresholds:
- **Sequential:** File count < 8 OR domain count < 2 OR file overlap > 30%
- **Parallel:** File count ≥ 8 AND domain count ≥ 2 AND file overlap < 30%

No manual configuration needed.

---

### Q: What if validation fails after 3 attempts?

**A:** Workflow continues (non-blocking). You should:
1. Review validation logs (`.workflow/outputs/EPIC-XXX/validation/`)
2. Fix issues manually
3. Run `npm run validate-all` to verify
4. Amend commit if needed
5. Review post-mortem for prevention strategies

---

### Q: Can I customize validation scripts?

**A:** Yes! Copy templates and customize:
```bash
cp -r ~/tier1_workflow_global/implementation/validation_scripts/ ./tools/
nano tools/validate_architecture.py
nano tools/validate_contracts.py
```

Then update `package.json`:
```json
{
  "scripts": {
    "validate-all": "npm run lint && npm run typecheck && python3 tools/validate_architecture.py"
  }
}
```

---

### Q: How do I handle merge conflicts in parallel execution?

**A:** Workflow detects conflicts and pauses:
```
⚠️ Merge conflicts detected in: backend, frontend

Manual resolution required:
  git merge feature/EPIC-XXX/backend
  # Resolve conflicts
  git add .
  git commit
```

After resolving:
```bash
npm run validate-all
/execute-workflow EPIC-XXX --resume  # (Resume not yet implemented - Week 5)
```

Currently: Complete workflow manually after conflict resolution.

---

### Q: Can I edit the prescriptive plan after creation?

**A:** Yes! Edit `file-tasks.md` before running workflow:
```bash
nano .tasks/backlog/EPIC-XXX-title/implementation-details/file-tasks.md
# Make changes
# Save and exit

/execute-workflow EPIC-XXX
```

Agents will follow the updated plan.

---

### Q: What if I don't have GitHub CLI installed?

**A:** GitHub integration is optional. Workflow will:
- Detect `gh` CLI unavailable
- Skip issue creation (log info message)
- Continue workflow normally
- Local `.tasks/` directory is source of truth

---

### Q: How do I apply post-mortem recommendations?

**A:**
1. Read full post-mortem: `cat .workflow/post-mortem/EPIC-XXX.md`
2. Review "Recommendations" section
3. For each recommendation:
   - Evaluate: Is it generally applicable?
   - Edit: Update referenced briefing file
   - Commit: Separate commit for briefing updates
4. Archive post-mortem (keep permanently for reference)

---

### Q: Can I use the workflow for non-Python projects?

**A:** Yes! Workflow supports:
- **Python:** ruff, mypy
- **TypeScript:** eslint, prettier, tsc
- **Go:** golangci-lint, gofmt
- **Mixed:** Configure `validate-all` script for all languages

Example polyglot `package.json`:
```json
{
  "scripts": {
    "validate-py": "ruff check . && mypy src/",
    "validate-ts": "eslint src/ && tsc --noEmit",
    "validate-go": "golangci-lint run && gofmt -l .",
    "validate-all": "npm run validate-py && npm run validate-ts && npm run validate-go"
  }
}
```

---

### Q: What's the difference between spec.md and file-tasks.md?

**A:**
- **spec.md:** WHAT to build (requirements, acceptance criteria)
- **architecture.md:** WHY and HOW (design decisions, components)
- **file-tasks.md:** EXACT IMPLEMENTATION (file paths, code snippets, line-by-line)

Agents read all three, but **file-tasks.md is the source of truth** for implementation.

---

### Q: How long does a typical workflow take?

**A:**

| Epic Size | Mode | Typical Duration |
|-----------|------|------------------|
| Small (5-7 files) | Sequential | 15-30 minutes |
| Medium (8-12 files) | Sequential | 30-45 minutes |
| Large (13-20 files) | Parallel (2-3 domains) | 25-40 minutes |
| X-Large (21+ files) | Parallel (3-4 domains) | 30-50 minutes |

Add 3-6 minutes for validation retry (if needed).

---

### Q: Can I run multiple workflows in parallel?

**A:** No (currently). Worktree creation requires clean git state. Future enhancement.

---

### Q: What if I need to pause the workflow?

**A:** Workflow cannot be paused mid-execution. If interrupted:
- **Phase 1:** Agents complete independently, results may be partial
- **Phase 3:** Validation loop may not complete
- **Phase 5:** Commit may not be created

**Recommendation:** Let workflow complete (~20-50 min), then review results.

---

## Summary

The Tier 1 workflow provides:

**Automation:**
- Spec → Plan → Implementation → Validation → Commit → Post-Mortem
- 2-4x speedup for large epics (parallel execution)
- Automated validation with retry loop

**Quality:**
- Agent briefings enforce project patterns
- Build fixer handles common errors
- Post-mortem captures learnings

**Flexibility:**
- Automatic sequential/parallel detection
- Customizable validation scripts
- Optional GitHub integration
- Manual intervention supported at every phase

**Best Practices:**
- Split epics >25 files
- Write specific prescriptive plans
- Organize by domain (minimize overlap)
- Review and apply post-mortem recommendations

**Next Steps:**
- Try the [Quick Start Guide](./WORKFLOW_QUICK_START.md) (5 minutes)
- Read the [Comprehensive Guide](./WORKFLOW_COMPREHENSIVE_GUIDE.md) (technical deep dive)
- Customize agent briefings for your project
- Set up validation scripts

---

**Generated:** 2025-10-19
**Version:** 1.0
**Author:** Claude Code (Tier 1 Workflow Documentation)
