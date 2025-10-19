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

## Post-Implementation Checklist

Before writing results JSON, verify:

- [ ] All business logic in `services/` (not in routes)
- [ ] All API routes delegate to services
- [ ] All functions have complete type hints
- [ ] All database operations use `async`/`await`
- [ ] Error handling added (custom exceptions + HTTPException in routes)
- [ ] Database transactions use try/except with rollback
- [ ] No tests written (per phase rules)
- [ ] Files match prescriptive plan exactly
- [ ] Code passes syntax check: `python -m py_compile <file>`
- [ ] Code passes lint check: `ruff check <file>`

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
