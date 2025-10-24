---
domain: backend
updated: 2025-10-19
applies_to: [implementation-agent-v1, build-fixer-agent-v1]
---

# Backend Implementation Briefing

This briefing provides domain-specific patterns and rules for backend implementation in this project.

## Project Architecture

**Technology Stack:**
- Language: Python 3.11+
- Framework: FastAPI
- Database: PostgreSQL (via SQLAlchemy ORM)
- Async: asyncio + asyncpg

**Design Philosophy:**
- Service layer pattern (business logic separate from API routes)
- Dependency injection via FastAPI `Depends()`
- Async/await everywhere for database operations
- Type hints mandatory for all functions
- Custom exceptions + HTTPException for error handling

## File Structure

```
src/backend/
├── api/                    # API routes (FastAPI routers)
│   ├── email_routes.py     # /api/emails endpoints
│   └── auth_routes.py      # /api/auth endpoints
├── services/               # Business logic layer
│   ├── email_service.py    # EmailService class
│   └── auth_service.py     # AuthService class
├── models/                 # SQLAlchemy ORM models
│   ├── email.py            # Email model
│   └── user.py             # User model
└── schemas/                # Pydantic schemas (request/response)
    ├── email.py            # EmailCreate, EmailResponse
    └── user.py             # UserCreate, UserResponse
```

**Naming Conventions:**
- Services: `EmailService`, `AuthService` (class names)
- Models: `Email`, `User` (singular nouns)
- Schemas: `EmailCreate`, `EmailResponse` (model name + action/type)
- Routes: `email_routes.py`, `auth_routes.py` (snake_case)

## Coding Patterns

### 1. Service Layer Pattern

ALL business logic goes in `services/` (not in API routes).

API routes are THIN wrappers that:
- Accept request data
- Instantiate service with dependencies
- Call service method
- Return response

**✅ CORRECT Example:**

```python
# services/email_service.py
class EmailService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_email(self, email_data: EmailCreate) -> Email:
        """Create new email. Business logic here."""
        # Validation
        if not email_data.subject:
            raise ValueError("Subject cannot be empty")

        # Business logic
        email = Email(**email_data.dict())
        self.db.add(email)
        await self.db.commit()
        await self.db.refresh(email)
        return email

# api/email_routes.py
@router.post("/emails", response_model=EmailResponse)
async def create_email(
    email_data: EmailCreate,
    db: AsyncSession = Depends(get_db)
):
    """API route delegates to service."""
    service = EmailService(db)
    email = await service.create_email(email_data)
    return email
```

**❌ WRONG Example:**

```python
# api/email_routes.py
@router.post("/emails")
async def create_email(email_data: EmailCreate, db: AsyncSession):
    # ❌ Business logic in route - should be in service!
    if not email_data.subject:
        raise HTTPException(400, "Subject required")

    email = Email(**email_data.dict())
    db.add(email)
    await db.commit()
    return email
```

### 2. Dependency Injection Pattern

Use FastAPI's `Depends()` for all dependencies.

**Database Session:**

```python
# ✅ CORRECT
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session."""
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/emails/{email_id}")
async def get_email(
    email_id: int,
    db: AsyncSession = Depends(get_db)  # ✅ Dependency injection
):
    service = EmailService(db)
    return await service.get_email(email_id)
```

**Current User:**

```python
# ✅ CORRECT
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get authenticated user from token."""
    # Verify token, fetch user
    return user

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)  # ✅ Injected
):
    return current_user
```

### 3. Error Handling

ALL service methods must handle errors with custom exceptions.

**Custom Exceptions:**

```python
# services/exceptions.py
class EmailNotFoundError(Exception):
    """Raised when email doesn't exist."""
    pass

class EmailValidationError(Exception):
    """Raised when email data is invalid."""
    pass

class DatabaseError(Exception):
    """Raised on database operation failures."""
    pass
```

**Service Layer:**

```python
# services/email_service.py
async def get_email(self, email_id: int) -> Email:
    """Get email by ID."""
    email = await self.db.get(Email, email_id)
    if not email:
        raise EmailNotFoundError(f"Email {email_id} not found")
    return email

async def delete_email(self, email_id: int) -> None:
    """Delete email by ID."""
    try:
        email = await self.get_email(email_id)
        await self.db.delete(email)
        await self.db.commit()
    except SQLAlchemyError as e:
        await self.db.rollback()
        raise DatabaseError(f"Failed to delete email: {e}")
```

**API Route Layer:**

```python
# api/email_routes.py
@router.get("/emails/{email_id}")
async def get_email(email_id: int, db: AsyncSession = Depends(get_db)):
    try:
        service = EmailService(db)
        return await service.get_email(email_id)
    except EmailNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Key Points:**
- Services raise CUSTOM exceptions (not HTTPException)
- Routes catch custom exceptions and convert to HTTPException
- Database errors always trigger rollback

### 4. Database Query Pattern

Use SQLAlchemy 2.0 style queries with `select()`.

**✅ CORRECT:**

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def list_emails(self, user_id: int, limit: int = 10) -> list[Email]:
    """List emails for user."""
    stmt = (
        select(Email)
        .where(Email.user_id == user_id)
        .options(selectinload(Email.attachments))  # Eager load
        .order_by(Email.created_at.desc())
        .limit(limit)
    )
    result = await self.db.execute(stmt)
    return result.scalars().all()
```

**❌ WRONG (Old SQLAlchemy 1.x style):**

```python
# ❌ Don't use query()
emails = db.query(Email).filter_by(user_id=user_id).limit(limit).all()
```

### 5. Transaction Pattern

Always use explicit transactions for multi-step operations.

**✅ CORRECT:**

```python
async def transfer_email(self, email_id: int, target_folder_id: int) -> Email:
    """Move email to different folder (transactional)."""
    try:
        # Step 1: Get email
        email = await self.get_email(email_id)

        # Step 2: Validate target folder exists
        folder = await self.db.get(Folder, target_folder_id)
        if not folder:
            raise FolderNotFoundError(f"Folder {target_folder_id} not found")

        # Step 3: Update email
        email.folder_id = target_folder_id
        email.updated_at = datetime.utcnow()

        # Step 4: Commit transaction
        await self.db.commit()
        await self.db.refresh(email)
        return email

    except Exception as e:
        await self.db.rollback()
        raise DatabaseError(f"Failed to transfer email: {e}")
```

**Key Points:**
- Multiple database operations = single transaction
- Always rollback on any exception
- Commit only when ALL steps succeed

### 6. Type Hints (MANDATORY)

ALL functions must have complete type hints.

**✅ CORRECT:**

```python
async def get_email(self, email_id: int) -> Email:
    """Get email by ID."""
    ...

async def list_emails(
    self,
    user_id: int,
    limit: int = 10,
    offset: int = 0
) -> list[Email]:
    """List emails for user."""
    ...

async def search_emails(
    self,
    query: str,
    filters: Optional[dict[str, Any]] = None
) -> list[Email]:
    """Search emails with optional filters."""
    ...
```

**❌ WRONG:**

```python
# ❌ Missing type hints
async def get_email(email_id):
    ...

# ❌ Incomplete type hints
async def list_emails(user_id: int):
    ...

# ❌ Missing return type
async def search_emails(query: str) -> list:  # Should be list[Email]
    ...
```

**Type Hint Requirements:**
- All function parameters must have types
- All return types must be specified
- Use `Optional[T]` for nullable types
- Use `list[T]`, `dict[K, V]` for collections
- Use `Any` sparingly (only when truly dynamic)

### Module-Level Type Annotations

**CRITICAL for mypy strict mode:** Module-level variables (especially empty collections) MUST have explicit type annotations.

**Pattern:**

When declaring module-level collections, lists, or dictionaries that start empty:
- Always provide explicit type annotations
- Use the format: `var_name: CollectionType[ElementType] = initial_value`

**✅ CORRECT Examples:**

```python
# Module-level lists
trace_plots: list[str] = []
figure_paths: list[Path] = []
analysis_results: list[dict[str, Any]] = []

# Module-level dictionaries
config_cache: dict[str, Any] = {}
data_store: dict[str, pd.DataFrame] = {}

# Module-level optional values
current_analysis: Optional[AnalysisResult] = None
```

**❌ WRONG Examples:**

```python
# ❌ Missing type annotation - mypy error: "Need type annotation for 'trace_plots'"
trace_plots = []

# ❌ Incomplete type annotation - mypy error: list of what?
figure_paths: list = []

# ❌ Too vague - dict of what to what?
config_cache: dict = {}
```

**mypy Error Explanation:**

When mypy sees `trace_plots = []`, it cannot infer whether this is:
- `list[str]`
- `list[int]`
- `list[Any]`
- `list[dict[str, str]]`

**Solution:** Always provide explicit type annotation for empty collections.

**Why it matters:**
- Enables type checking throughout the module
- Prevents accidental type violations
- Self-documenting code (clear what types are expected)
- Required for mypy strict mode compliance

**When to use:**
- All module-level variables
- All class-level attributes (if not initialized in `__init__`)
- Any empty collection that will be populated later

## Common Mistakes to Avoid

### 1. Business Logic in Routes

❌ **WRONG:**
```python
@router.post("/emails")
async def create_email(email_data: EmailCreate, db: AsyncSession):
    # ❌ Validation logic in route
    if not email_data.subject:
        raise HTTPException(400, "Subject required")

    # ❌ Database operations in route
    email = Email(**email_data.dict())
    db.add(email)
    await db.commit()
    return email
```

✅ **CORRECT:**
```python
@router.post("/emails")
async def create_email(email_data: EmailCreate, db: AsyncSession = Depends(get_db)):
    service = EmailService(db)  # ✅ Delegate to service
    return await service.create_email(email_data)
```

### 2. Missing Error Handling

❌ **WRONG:**
```python
async def get_email(self, email_id: int) -> Email:
    # ❌ No error handling - will crash if not found
    email = await self.db.get(Email, email_id)
    return email
```

✅ **CORRECT:**
```python
async def get_email(self, email_id: int) -> Email:
    email = await self.db.get(Email, email_id)
    if not email:
        raise EmailNotFoundError(f"Email {email_id} not found")
    return email
```

### 3. Forgetting Async/Await

❌ **WRONG:**
```python
async def get_email(self, email_id: int) -> Email:
    # ❌ Missing await - will return coroutine instead of result
    email = self.db.get(Email, email_id)
    return email
```

✅ **CORRECT:**
```python
async def get_email(self, email_id: int) -> Email:
    email = await self.db.get(Email, email_id)  # ✅ Await async operation
    return email
```

### 4. Missing Type Hints

❌ **WRONG:**
```python
# ❌ No type hints
async def list_emails(user_id, limit=10):
    ...
```

✅ **CORRECT:**
```python
async def list_emails(self, user_id: int, limit: int = 10) -> list[Email]:
    ...
```

### 5. Writing Tests in Implementation Phase

❌ **WRONG:**
```python
# implementation agent writes:
# - src/services/email_service.py
# - tests/test_email_service.py  ❌ DON'T WRITE TESTS
```

✅ **CORRECT:**
```python
# implementation agent writes ONLY:
# - src/services/email_service.py  ✅ Implementation only
```

**Reason:** Implementation phase does NOT write tests. Testing phase handles this (if project requires it).

## 7. Pre-Validation Linting Pattern

**Source:** EPIC-002 post-mortem (clinical-eda-pipeline)

**CRITICAL workflow change:** Always run linting BEFORE validation to prevent validation failures.

### The Problem

**Before this pattern:**
- Implementation agent writes code → Validation agent runs tests
- Tests fail due to linting issues (unused imports, f-string formatting)
- Build fixer agent invoked (unnecessary overhead)

**Root cause:** Linting issues treated as "build failures" when they're really "code quality" issues that should be auto-fixed during implementation.

### The Solution

**New workflow:** Implementation → Auto-lint → Validation

**Pattern:**

After writing code but BEFORE marking task complete:

1. **Run auto-fix linting:**
   ```bash
   ruff check --fix .
   ```

2. **Verify linting passed:**
   ```bash
   ruff check .
   ```

3. **If linting errors remain** (cannot auto-fix):
   - Fix manually
   - Re-run `ruff check .`
   - Repeat until clean

4. **THEN mark task complete** for validation

**Why this works:**

- **Prevents validation failures:** Linting issues fixed before tests run
- **Reduces build fixer overhead:** No need to invoke build fixer for simple linting
- **Faster iteration:** Auto-fix handles 90%+ of linting issues automatically
- **Cleaner git history:** Linting fixes included in initial commit

**Common auto-fixable issues:**
- F401: Unused imports (removed automatically)
- F541: f-string without placeholders (f-prefix removed automatically)
- I001: Import sorting (reordered automatically)
- UP: Syntax upgrades (e.g., `List[str]` → `list[str]`)
- W291/W293: Whitespace issues (trimmed automatically)

**Manual fixes required for:**
- Missing type annotations (e.g., `trace_plots: list[str] = []`)
- Type hint errors (wrong types, missing generics)
- Complex refactoring (large functions, duplicate code)

### Integration with Validation Phase

**Validation agent expectations:**

1. **Linting MUST be clean** before validation runs
2. **If linting fails during validation:**
   - This is an implementation bug (implementation didn't follow pre-validation pattern)
   - Validation agent can run `ruff check --fix .` as a courtesy
   - But this should be RARE (not expected workflow)

**Build fixer agent role:**

Build fixer should NOT be invoked for simple linting issues. Build fixer handles:
- Test failures (logic errors, incorrect behavior)
- Type checking failures (complex type inference issues)
- Integration issues (module compatibility)

**NOT:**
- Unused imports (implementation should auto-fix)
- Missing type annotations (implementation should catch)
- Import sorting (auto-fixable)

**Linting command reference:**

```bash
# Auto-fix most issues (safe, non-destructive)
ruff check --fix .

# Verify linting clean (exit code 0 = success)
ruff check .

# Show specific linting errors (if verification fails)
ruff check . --output-format=text
```

## 🚫 CRITICAL: Agent Failure Reporting Protocol

**Source:** EPIC-013 post-mortem analysis (email_management_system)
**Applies to:** ALL implementation agents

### The Problem This Solves

**EPIC-013 Failure Mode:**
- Spec required: `claude-agent-sdk` package from specific source
- Agent tried: `pip install claude-agent-sdk` → Package not found
- Agent response: Created ENTIRE mocked infrastructure (simulation functions, hardcoded responses)
- Result: Tests passed against fake code, task marked "complete", massive waste of time/tokens

**Root cause:** Agent improvised when fundamentally blocked instead of reporting the blocker.

### Blocker Definition

A **blocker** is when:
1. Specification requires resource X (package, API, service, file)
2. You cannot access/find X using available tools
3. Proceeding without X would require improvisation/simulation
4. No alternative approach achieves the same functional result

### Examples: Blocker vs. Solvable

**✅ BLOCKERS (must report, cannot proceed):**
- Package not found in PyPI as specified: `pip install claude-agent-sdk` → Not found
- API endpoint returns 404 with no alternative: `POST /api/v2/complete` → 404
- Authentication fails despite correct credentials: `API_KEY=xxx` → 401 Unauthorized
- Service not running: `curl http://localhost:8000/health` → Connection refused
- Required file doesn't exist: Spec says "use config/database.yaml" → File not found

**❌ NOT BLOCKERS (solvable, proceed with problem-solving):**
- Need different import path: Try `from foo import bar` → Try `from foo.bar import baz`
- Minor syntax error: Fix and retry
- Test fails: Debug, identify issue, fix root cause
- Type hint error: Investigate types, add correct annotations
- Linting issue: Run `ruff check --fix .`, address remaining issues

**Key distinction:** Can you solve this with available tools and knowledge? YES = not a blocker. NO = blocker.

### 🚫 ABSOLUTE PROHIBITION: No Improvisation When Blocked

If you encounter a blocker, you are **FORBIDDEN** from:

- ❌ Creating simulation/stub implementations (`def _simulate_*`, `def _mock_*`, `def _fake_*`)
- ❌ Returning hardcoded/pattern-based data (if "keyword" in prompt: return "hardcoded")
- ❌ Writing tests that validate mocks instead of real behavior
- ❌ Marking task complete when functionality doesn't work
- ❌ Saying "I'll fake it for now and come back later"
- ❌ Creating placeholder implementations with TODOs
- ❌ Improvising alternative approaches not in specification

**Why this is critical:**
- Mocked code wastes tokens on useless implementation
- Tests pass against fake functionality (false confidence)
- Validation phase doesn't catch the issue (no real tests)
- Human discovers broken functionality much later
- Massive cleanup required to remove simulation code

### ✅ REQUIRED: Stop and Report

When you encounter a blocker, you **MUST**:

1. ✅ **Stop immediately** - Do not proceed with improvisation
2. ✅ **Output blocker report** - Use standardized format below
3. ✅ **Mark task as BLOCKED** - NOT "complete", NOT "in progress"
4. ✅ **Preserve diagnostic info** - Include error messages, commands tried, outputs

### Blocker Report Format

Use this exact format in your output:

```
🚫 BLOCKER DETECTED 🚫

**Blocker Type:** [Package Not Found | API Error | Auth Failure | Service Unavailable | File Not Found]

**What was expected:**
- [Specific requirement from spec/task file]
- [Exact resource/package/endpoint expected]
- [Where it was supposed to be found]

**What actually happened:**
- [Specific error encountered]
- [Exact command that failed]
- [Error message/output received]

**Tools/methods attempted:**
- [Command 1: result]
- [Command 2: result]
- [Command 3: result]

**Cannot proceed because:**
- [Why this blocks functional implementation]
- [What would need to be mocked/simulated to proceed]
- [Why alternative approaches won't achieve spec requirements]

**Awaiting human intervention to:**
- [ ] Verify package name/source is correct
- [ ] Provide correct installation instructions
- [ ] Update specification if alternative approach needed
- [ ] Provide credentials/access if auth issue
- [ ] Start required service if service unavailable

**Task Status:** BLOCKED (not proceeding with implementation)
```

### Example Blocker Report #1: Package Not Found

```
🚫 BLOCKER DETECTED 🚫

**Blocker Type:** Package Not Found

**What was expected:**
- Specification (file-tasks.md, line 45) requires: `claude-agent-sdk` package
- Installation command: `pip install claude-agent-sdk`
- Expected source: PyPI

**What actually happened:**
- Command: `pip install claude-agent-sdk`
- Error: "ERROR: Could not find a version that satisfies the requirement claude-agent-sdk"
- Exit code: 1

**Tools/methods attempted:**
- `pip install claude-agent-sdk` → Not found
- `pip search claude-agent` → No results
- `pip search agent-sdk` → No results
- Checked specification for alternative source → None specified

**Cannot proceed because:**
- The entire service implementation depends on this SDK
- Creating a mock implementation would require inventing the SDK's API
- Tests would validate fake functionality instead of real integration
- This violates the prohibition on simulation/improvisation

**Awaiting human intervention to:**
- [ ] Verify the package name is correct (could it be `claude_agent_sdk` or `anthropic-agent-sdk`?)
- [ ] Provide correct installation command if package is from GitHub/private registry
- [ ] Update specification if we should use a different library
- [ ] Confirm package is publicly available or provide access credentials

**Task Status:** BLOCKED (not proceeding with implementation)
```

### Example Blocker Report #2: API Error

```
🚫 BLOCKER DETECTED 🚫

**Blocker Type:** API Error

**What was expected:**
- Specification requires calling: `POST https://api.service.com/v2/complete`
- Expected: 200 OK with JSON response
- Authentication: API key from environment variable

**What actually happened:**
- Command: `curl -X POST https://api.service.com/v2/complete -H "Authorization: Bearer $API_KEY"`
- Response: 404 Not Found
- Body: {"error": "Endpoint not found"}

**Tools/methods attempted:**
- `POST /v2/complete` → 404
- `POST /v1/complete` → 404 (tried older version)
- `GET /v2/complete` → 404 (tried different method)
- Checked API documentation URL in spec → Page not found (404)

**Cannot proceed because:**
- Service integration requires this specific endpoint
- Creating a fake API response would simulate functionality
- Tests would pass but real integration would fail in production

**Awaiting human intervention to:**
- [ ] Verify the API endpoint URL is correct
- [ ] Check if API documentation has moved
- [ ] Confirm API is accessible (could be network/firewall issue)
- [ ] Update specification with correct endpoint if it has changed

**Task Status:** BLOCKED (not proceeding with implementation)
```

### When to Use This Protocol

**Use blocker reporting when:**
- External resource required by spec cannot be accessed
- No reasonable alternative exists within project constraints
- Proceeding would require inventing/mocking functionality

**Do NOT use blocker reporting for:**
- Normal debugging (syntax errors, type issues, logic bugs)
- Solvable problems (wrong import path, missing dependency declaration)
- Optimization issues (slow query, inefficient algorithm)
- Test failures (these are expected, debug and fix)

**If uncertain:** Ask yourself: "Can I solve this without inventing functionality?"
- YES → Not a blocker, solve it
- NO → Blocker, report it

### Integration with Workflow

**After blocker report:**
1. Agent outputs blocker report in standardized format
2. Agent marks task as BLOCKED in results JSON
3. Orchestrator detects blocked status → pauses workflow
4. Human reviews blocker → provides resolution
5. Workflow resumes with corrected information

**Validation pipeline includes:**
- Automated detection of simulation patterns (see `scripts/detect_simulation_code.py`)
- Reality checks in tests to prove real external integration
- Blocker report parsing to track and resolve blockers systematically

### Success Criteria

This protocol succeeds when:
- Zero simulation code appears in codebase (validated by detection script)
- 100% of genuine blockers are reported using this format
- Human intervention resolves blockers within SLA (e.g., 24 hours)
- No "EPIC-013 style" failures occur (mocked implementations passing validation)

**Your responsibility:** Report blockers immediately. Do not improvise. Do not simulate. Do not guess.

---

## Post-Implementation Checklist

Before writing results JSON, verify:

- [ ] All business logic in `services/` (not in routes)
- [ ] All API routes delegate to services
- [ ] All functions have complete type hints
- [ ] **Module-level variables have explicit type annotations** ✅ NEW
- [ ] All database operations use `async`/`await`
- [ ] Error handling added (custom exceptions + HTTPException in routes)
- [ ] Database transactions use try/except with rollback
- [ ] No tests written (per phase rules)
- [ ] Files match prescriptive plan exactly
- [ ] **Code passes auto-fix linting: `ruff check --fix .`** ✅ NEW
- [ ] **Code passes linting verification: `ruff check .`** ✅ NEW
- [ ] Code passes syntax check: `python -m py_compile <file>` (if linting passes, this usually does too)

## Questions to Ask if Unclear

If the prescriptive plan is unclear about:

**Type hints:**
- "What is the return type for this async function?"
- "Should this parameter be Optional[T] or just T?"

**Error handling:**
- "Should this operation raise a custom exception or HTTPException?"
- "What error code should be returned for this failure case?"

**Service methods:**
- "Should this be async or sync?" (Default: async for database operations)
- "Should this method commit or let the caller commit?"

**Database queries:**
- "Should relationships be eager-loaded (selectinload) or lazy-loaded?"
- "Should this query use pagination (limit/offset)?"

**Validation:**
- "Should validation happen in service or Pydantic schema?"
- "What are the validation rules for this field?"

**Note these questions in your results JSON under `clarifications_needed`.** The orchestrator will review and provide guidance.
