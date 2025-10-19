---
type: project-architecture
applies_to: all
updated: 2025-10-19
---

# Project Architecture Reference

This document defines project-wide architectural patterns, coding standards, and conventions that apply to ALL domains (backend, frontend, database, etc.).

**Purpose:** Ensure consistent code quality and architectural decisions across the entire project.

**Who should read this:** All implementation agents, regardless of domain specialization.

---

## Project Overview

**Project Name:** [YOUR PROJECT NAME]

**Technology Stack:**
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** [e.g., React, TypeScript, Tailwind CSS] (if applicable)
- **Database:** [PostgreSQL, MySQL, etc.]
- **Testing:** pytest, pytest-cov (optional)
- **Deployment:** [Docker, Kubernetes, etc.] (if applicable)

**Architecture Style:**
- **Pattern:** Layered architecture (API → Service → Data)
- **Design:** Domain-driven design (DDD) principles
- **API:** RESTful HTTP/JSON
- **Authentication:** [JWT, OAuth2, etc.] (if applicable)

---

## Directory Structure

### Standard Layout

```
<project-root>/
├── src/                        # Source code
│   ├── backend/                # Backend application
│   │   ├── api/                # API routes (thin wrappers)
│   │   ├── services/           # Business logic
│   │   ├── models/             # Database models (SQLAlchemy)
│   │   ├── schemas/            # Request/response schemas (Pydantic)
│   │   ├── core/               # Config, dependencies, utilities
│   │   └── main.py             # Application entry point
│   ├── frontend/               # Frontend application (if applicable)
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── hooks/              # Custom React hooks
│   │   └── utils/              # Frontend utilities
│   └── shared/                 # Shared code (types, constants)
├── tests/                      # Test files (mirror src/ structure)
│   ├── backend/
│   └── frontend/
├── docs/                       # Documentation
├── tools/                      # Development tools
│   ├── validate_architecture.py
│   └── validate_contracts.py
├── .tasks/                     # Task management (epics)
├── .workflow/                  # Workflow execution artifacts
├── pyproject.toml              # Python dependencies + config
├── package.json                # npm scripts for validation
└── README.md                   # Project documentation
```

**Key Principles:**
- **Separation of concerns:** API, business logic, and data access are separate layers
- **Mirror structure:** Test directory structure mirrors `src/` structure
- **Domain grouping:** Group by domain (backend, frontend) then by layer (api, services)

---

## Code Organization Principles

### 1. Layered Architecture

**Layers (top to bottom):**

1. **API Layer** (`src/backend/api/`)
   - FastAPI routes and routers
   - Request/response handling
   - Input validation (Pydantic schemas)
   - Delegates to service layer

2. **Service Layer** (`src/backend/services/`)
   - Business logic and domain rules
   - Orchestrates multiple data operations
   - Raises custom exceptions
   - No direct HTTP knowledge

3. **Data Layer** (`src/backend/models/`)
   - SQLAlchemy ORM models
   - Database schema definitions
   - Relationships and constraints

**✅ CORRECT Flow:**
```
Client Request → API Route → Service Method → Database Model → Response
```

**❌ WRONG Flow:**
```
Client Request → API Route → Database Model → Response
                     ↑
               (business logic here - NO!)
```

### 2. Dependency Rules

**Golden Rule:** Dependencies flow DOWNWARD only.

```
API Layer (depends on ↓)
    ↓
Service Layer (depends on ↓)
    ↓
Data Layer (no dependencies on upper layers)
```

**✅ ALLOWED:**
- API routes import services
- Services import models
- Services import schemas (for type hints)

**❌ FORBIDDEN:**
- Models import services
- Models import API routes
- Services import API routes

### 3. Single Responsibility Principle

Each module/class has ONE responsibility:

**✅ CORRECT:**
```python
# email_service.py - handles email business logic
# user_service.py - handles user business logic
# auth_service.py - handles authentication logic
```

**❌ WRONG:**
```python
# utils.py - contains email logic, user logic, auth logic, etc.
```

### 4. Naming Conventions

**Python (backend):**
- **Modules:** `snake_case.py` (e.g., `email_service.py`)
- **Classes:** `PascalCase` (e.g., `EmailService`)
- **Functions/methods:** `snake_case` (e.g., `create_email()`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_EMAIL_SIZE`)
- **Private:** `_leading_underscore` (e.g., `_validate_email()`)

**TypeScript (frontend):**
- **Components:** `PascalCase.tsx` (e.g., `EmailList.tsx`)
- **Hooks:** `camelCase` starting with `use` (e.g., `useEmailData`)
- **Utils:** `camelCase.ts` (e.g., `formatDate.ts`)

---

## Error Handling Strategy

### Custom Exceptions

Define domain-specific exceptions in each service:

```python
# services/exceptions.py
class DomainException(Exception):
    """Base exception for domain errors."""
    pass

class ResourceNotFoundError(DomainException):
    """Resource doesn't exist."""
    pass

class ValidationError(DomainException):
    """Input validation failed."""
    pass

class UnauthorizedError(DomainException):
    """User not authorized for operation."""
    pass

class DatabaseError(DomainException):
    """Database operation failed."""
    pass
```

### Error Handling Pattern

**Service Layer:**
```python
# services/email_service.py
async def get_email(self, email_id: int) -> Email:
    """Get email by ID."""
    email = await self.db.get(Email, email_id)
    if not email:
        raise ResourceNotFoundError(f"Email {email_id} not found")
    return email
```

**API Layer:**
```python
# api/email_routes.py
@router.get("/emails/{email_id}")
async def get_email(email_id: int, db: AsyncSession = Depends(get_db)):
    try:
        service = EmailService(db)
        return await service.get_email(email_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Key Points:**
- Services raise CUSTOM exceptions
- API routes catch and convert to HTTPException
- Database errors trigger rollback

---

## Logging and Monitoring

### Logging Standards

**Use Python's logging module:**

```python
import logging

logger = logging.getLogger(__name__)

# Service method
async def create_email(self, email_data: EmailCreate) -> Email:
    logger.info(f"Creating email: {email_data.subject}")
    try:
        email = Email(**email_data.dict())
        self.db.add(email)
        await self.db.commit()
        logger.info(f"Email created: {email.id}")
        return email
    except Exception as e:
        logger.error(f"Failed to create email: {e}")
        raise
```

**Log Levels:**
- **DEBUG:** Detailed diagnostic information
- **INFO:** General informational messages (e.g., "Email created")
- **WARNING:** Unexpected but recoverable issues
- **ERROR:** Error events that still allow operation to continue
- **CRITICAL:** Serious errors causing operation failure

**What to Log:**
- ✅ Important business operations (create, update, delete)
- ✅ Authentication events (login, logout)
- ✅ Error conditions with context
- ❌ Sensitive data (passwords, tokens, PII)
- ❌ Every single function call (too noisy)

---

## Testing Philosophy

### Testing Strategy for Tier 1 Projects

**IMPORTANT:** Most Tier 1 projects do NOT require comprehensive testing phase.

**Rationale:**
- Tests written by agents often provide false confidence
- Many agent-written tests pass without finding real issues
- Manual testing + validation phase catches most problems

**What We DO Test (if applicable):**
- ✅ Critical business logic (payment processing, security)
- ✅ Complex algorithms (search, ranking, calculations)
- ✅ Integration points (external APIs, database)

**What We DON'T Require:**
- ❌ Unit tests for every function
- ❌ 100% code coverage targets
- ❌ Tests written by implementation agents

**Testing Hooks for Implementation Agents:**

**DO NOT implement tests during implementation phase.**

If project requires tests:
- Tests are written in a SEPARATE testing phase (after implementation)
- Implementation agents focus ONLY on production code
- Testing agents (if used) write tests after reviewing implementation

---

## Documentation Standards

### What to Document

**Code Documentation (Docstrings):**

```python
async def create_email(self, email_data: EmailCreate) -> Email:
    """
    Create a new email.

    Args:
        email_data: Email data from request

    Returns:
        Created email object

    Raises:
        ValidationError: If email data is invalid
        DatabaseError: If database operation fails
    """
    ...
```

**✅ Document:**
- Public API methods (service layer + API routes)
- Complex business logic
- Non-obvious design decisions
- Error conditions

**❌ Don't Document:**
- Obvious getters/setters
- Self-explanatory utility functions
- Internal implementation details

### Markdown Documentation

**README.md:**
- Project overview
- Setup instructions
- Development workflow
- Deployment guide

**ARCHITECTURE.md:**
- System architecture diagrams
- Technology choices
- Design patterns
- Architectural decisions

**API.md:**
- API endpoint documentation
- Request/response examples
- Authentication requirements

**Note:** Documentation is updated MANUALLY (not auto-generated). Implementation agents do NOT write documentation.

---

## Performance Considerations

### Database Query Optimization

**Use Indexes:**
```python
# models/email.py
class Email(Base):
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)  # ✅ Index
    subject: Mapped[str] = mapped_column(String(255), index=True)  # ✅ Index for searches
    created_at: Mapped[datetime] = mapped_column(index=True)  # ✅ Index for sorting
```

**Eager Loading:**
```python
# ✅ CORRECT: Eager load relationships
stmt = (
    select(Email)
    .options(selectinload(Email.attachments))  # Load attachments
    .where(Email.user_id == user_id)
)

# ❌ WRONG: N+1 query problem
emails = await self.db.execute(select(Email))
for email in emails:
    attachments = email.attachments  # Separate query per email!
```

**Pagination:**
```python
async def list_emails(
    self,
    user_id: int,
    limit: int = 10,
    offset: int = 0
) -> list[Email]:
    """List emails with pagination."""
    stmt = (
        select(Email)
        .where(Email.user_id == user_id)
        .limit(limit)      # ✅ Limit results
        .offset(offset)    # ✅ Skip already fetched
    )
    result = await self.db.execute(stmt)
    return result.scalars().all()
```

### Async/Await Best Practices

**Use async for I/O operations:**
```python
# ✅ CORRECT
async def send_email(self, email: Email) -> None:
    """Send email asynchronously."""
    await smtp_client.send(email)  # Network I/O

# ❌ WRONG (blocks event loop)
def send_email(self, email: Email) -> None:
    """Send email synchronously."""
    smtp_client.send_sync(email)  # Blocks!
```

---

## Security Patterns

### Authentication & Authorization

**JWT Token Pattern:**
```python
# core/security.py
from jose import jwt

def create_access_token(user_id: int) -> str:
    """Create JWT access token."""
    payload = {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get authenticated user from token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload["sub"])
        # Fetch user from database
        return user
    except JWTError:
        raise UnauthorizedError("Invalid token")
```

**Route Protection:**
```python
# api/email_routes.py
@router.get("/emails")
async def list_emails(
    current_user: User = Depends(get_current_user),  # ✅ Protected route
    db: AsyncSession = Depends(get_db)
):
    service = EmailService(db)
    return await service.list_emails(current_user.id)
```

### Input Validation

**Use Pydantic schemas:**
```python
# schemas/email.py
from pydantic import BaseModel, EmailStr, validator

class EmailCreate(BaseModel):
    subject: str
    body: str
    recipient: EmailStr  # ✅ Validates email format

    @validator("subject")
    def subject_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Subject cannot be empty")
        return v
```

### SQL Injection Prevention

**✅ CORRECT (parameterized queries):**
```python
stmt = select(Email).where(Email.subject == user_input)  # ✅ Safe
```

**❌ WRONG (string concatenation):**
```python
query = f"SELECT * FROM emails WHERE subject = '{user_input}'"  # ❌ SQL injection!
```

---

## Deployment Considerations

### Environment-Specific Configuration

**Use environment variables:**
```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

**Environment files:**
- `.env.development` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment

**Never commit:**
- ❌ `.env` files with secrets
- ❌ Database credentials
- ❌ API keys

### Docker Deployment

**Dockerfile (if applicable):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY src/ ./src/

CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Agent Instructions

### For Implementation Agents

**You MUST:**
- ✅ Follow layered architecture (API → Service → Data)
- ✅ Use dependency injection (FastAPI `Depends()`)
- ✅ Add complete type hints to all functions
- ✅ Handle errors with custom exceptions
- ✅ Use async/await for database operations
- ✅ Follow naming conventions

**You MUST NOT:**
- ❌ Put business logic in API routes
- ❌ Write tests (testing phase handles this)
- ❌ Write documentation (manual updates preferred)
- ❌ Skip error handling
- ❌ Use synchronous database operations

### For Build Fixer Agents

**You MUST:**
- ✅ Fix ALL build/lint errors before completing
- ✅ Run validation scripts: `npm run lint:py && npm run format:py:check`
- ✅ Fix type errors: Add missing type hints
- ✅ Fix import errors: Use correct import paths
- ✅ Keep fixes surgical (don't refactor unrelated code)

**You MUST NOT:**
- ❌ Skip errors (fix ALL, not some)
- ❌ Comment out failing code
- ❌ Weaken type hints to pass mypy
- ❌ Disable linting rules

---

## Common Anti-Patterns to Avoid

### 1. God Objects

❌ **WRONG:**
```python
# services/app_service.py
class AppService:
    # ❌ Does everything - email, user, auth, etc.
    def create_email(self): ...
    def create_user(self): ...
    def login(self): ...
```

✅ **CORRECT:**
```python
# services/email_service.py
class EmailService:
    # ✅ Single responsibility
    def create_email(self): ...

# services/user_service.py
class UserService:
    def create_user(self): ...
```

### 2. Tight Coupling

❌ **WRONG:**
```python
# models/email.py
from services.email_service import EmailService  # ❌ Model depends on service!

class Email(Base):
    def send(self):
        EmailService().send(self)  # ❌ Tight coupling
```

✅ **CORRECT:**
```python
# services/email_service.py
class EmailService:
    def send_email(self, email: Email):  # ✅ Service operates on model
        ...
```

### 3. Magic Numbers

❌ **WRONG:**
```python
if len(email.subject) > 255:  # ❌ What is 255?
    raise ValidationError()
```

✅ **CORRECT:**
```python
MAX_SUBJECT_LENGTH = 255  # ✅ Named constant

if len(email.subject) > MAX_SUBJECT_LENGTH:
    raise ValidationError(f"Subject exceeds {MAX_SUBJECT_LENGTH} characters")
```

---

## Questions to Escalate

If you encounter these situations during implementation, note in results JSON under `clarifications_needed`:

**Architecture:**
- "Should this be a new service class or added to existing service?"
- "Does this operation require a new database model?"
- "Should this endpoint be RESTful or RPC-style?"

**Performance:**
- "Should this query use eager loading or lazy loading?"
- "Should this operation be synchronous or asynchronous?"
- "Should we add caching for this data?"

**Security:**
- "Should this endpoint require authentication?"
- "What permission level is required for this operation?"
- "Should we validate/sanitize this user input?"

**Error Handling:**
- "What HTTP status code for this error?"
- "Should this failure be logged as ERROR or WARNING?"
- "Should this operation retry on failure?"

---

## Summary

**Core Principles:**
1. **Layered architecture** - API → Service → Data
2. **Dependency injection** - Use FastAPI `Depends()`
3. **Type safety** - Complete type hints everywhere
4. **Error handling** - Custom exceptions + HTTPException
5. **Async/await** - All database operations async
6. **Single responsibility** - One class/module = one purpose
7. **Documentation** - Manual updates, not auto-generated
8. **Testing** - Optional, not required for implementation phase

**Remember:** This is a TEMPLATE. Customize for your project's specific needs.
