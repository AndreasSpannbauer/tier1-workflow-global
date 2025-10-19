# Workflow Customization Guide

**Last Updated:** 2025-10-19
**Status:** Production Ready
**Location:** `~/tier1_workflow_global/implementation/`

---

## Overview

This guide shows how to customize the Tier 1 workflow command for your project's specific needs. Customizations include:

1. **Agent Briefings** - Domain-specific patterns and conventions
2. **Validation Scripts** - Linting, type checking, testing
3. **Commit Messages** - Conventional commit formatting
4. **Parallel Detection** - Thresholds for parallel execution
5. **Post-Mortem Analysis** - Optional continuous improvement

---

## 1. Customize Agent Briefings

Agent briefings provide domain-specific patterns that guide implementation agents. These are the most important customizations for your project.

### Location

**Project-specific briefings:**
```
.claude/agent_briefings/
├── backend_implementation.md
├── project_architecture.md
└── [custom_domain].md
```

### Backend Implementation Briefing

**File:** `.claude/agent_briefings/backend_implementation.md`

#### Step 1: Update Technology Stack

**Original (FastAPI + PostgreSQL):**
```markdown
**Technology Stack:**
- Language: Python 3.11+
- Framework: FastAPI
- Database: PostgreSQL (via SQLAlchemy ORM)
- Async: asyncio + asyncpg
```

**Example 1: Flask + MySQL**
```markdown
**Technology Stack:**
- Language: Python 3.9+
- Framework: Flask
- Database: MySQL (via SQLAlchemy ORM)
- Async: N/A (synchronous)
```

**Example 2: Express.js + MongoDB**
```markdown
**Technology Stack:**
- Language: TypeScript 5+
- Framework: Express.js
- Database: MongoDB (via Mongoose ODM)
- Async: async/await (native promises)
```

**Example 3: Django + PostgreSQL**
```markdown
**Technology Stack:**
- Language: Python 3.10+
- Framework: Django 4.2+
- Database: PostgreSQL (via Django ORM)
- Async: Django async views (ASGI)
```

#### Step 2: Update File Structure

**Original (FastAPI):**
```markdown
src/backend/
├── api/                    # API routes (FastAPI routers)
├── services/               # Business logic layer
├── models/                 # SQLAlchemy ORM models
└── schemas/                # Pydantic schemas (request/response)
```

**Example 1: Flask**
```markdown
backend/
├── routes/                 # Flask blueprints
├── services/               # Business logic layer
├── models/                 # SQLAlchemy models
└── schemas/                # Marshmallow schemas
```

**Example 2: Express.js**
```markdown
src/
├── routes/                 # Express routes
├── controllers/            # Request handlers
├── services/               # Business logic
├── models/                 # Mongoose models
└── types/                  # TypeScript interfaces
```

**Example 3: Django**
```markdown
apps/
└── [app_name]/
    ├── views.py            # Django views
    ├── models.py           # Django models
    ├── serializers.py      # DRF serializers
    ├── services.py         # Business logic
    └── urls.py             # URL routing
```

#### Step 3: Update Coding Patterns

**Service Layer Pattern (Framework-Specific):**

**FastAPI (Original):**
```markdown
### Service Layer Pattern

ALL business logic goes in `services/` (not in API routes).

**Example:**
```python
# services/email_service.py
class EmailService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_email(self, email_data: EmailCreate) -> Email:
        email = Email(**email_data.dict())
        self.db.add(email)
        await self.db.commit()
        return email
```
```

**Flask (Synchronous):**
```markdown
### Service Layer Pattern

ALL business logic goes in `services/` (not in routes).

**Example:**
```python
# services/email_service.py
class EmailService:
    def __init__(self, db: Session):
        self.db = db

    def create_email(self, email_data: EmailCreate) -> Email:
        email = Email(**email_data.dict())
        self.db.add(email)
        self.db.commit()
        self.db.refresh(email)
        return email
```
```

**Express.js (TypeScript):**
```markdown
### Service Layer Pattern

ALL business logic goes in `services/` (not in controllers).

**Example:**
```typescript
// services/EmailService.ts
export class EmailService {
  async createEmail(emailData: EmailCreate): Promise<Email> {
    const email = new Email(emailData);
    await email.save();
    return email;
  }
}
```
```

**Django:**
```markdown
### Service Layer Pattern

ALL business logic goes in `services.py` (not in views).

**Example:**
```python
# apps/emails/services.py
class EmailService:
    @staticmethod
    def create_email(email_data: dict) -> Email:
        email = Email.objects.create(**email_data)
        return email
```
```

#### Step 4: Update Error Handling

**Framework-Specific Exception Handling:**

**FastAPI (Original):**
```markdown
### Error Handling

**Custom Exceptions:**
```python
class EmailNotFoundError(Exception):
    """Raised when email doesn't exist."""
    pass
```

**API Routes:**
```python
@router.get("/emails/{id}")
async def get_email(id: int):
    try:
        return await service.get_email(id)
    except EmailNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```
```

**Flask:**
```markdown
### Error Handling

**Custom Exceptions:**
```python
class EmailNotFoundError(Exception):
    """Raised when email doesn't exist."""
    pass
```

**Routes:**
```python
@bp.route("/emails/<int:id>", methods=["GET"])
def get_email(id):
    try:
        return jsonify(service.get_email(id))
    except EmailNotFoundError as e:
        abort(404, description=str(e))
```
```

**Express.js:**
```markdown
### Error Handling

**Custom Errors:**
```typescript
class EmailNotFoundError extends Error {
  statusCode = 404;
  constructor(message: string) {
    super(message);
  }
}
```

**Routes:**
```typescript
router.get("/emails/:id", async (req, res, next) => {
  try {
    const email = await service.getEmail(req.params.id);
    res.json(email);
  } catch (error) {
    if (error instanceof EmailNotFoundError) {
      res.status(404).json({ error: error.message });
    } else {
      next(error);
    }
  }
});
```
```

#### Step 5: Add Project-Specific Conventions

**Add your team's conventions:**

```markdown
## Project-Specific Conventions

### Naming Conventions

**Files:**
- Services: `email_service.py` (snake_case)
- Models: `email.py` (singular noun)
- Routes: `email_routes.py` (plural noun)

**Classes:**
- Services: `EmailService` (PascalCase + "Service")
- Models: `Email` (PascalCase, singular)
- Schemas: `EmailCreate`, `EmailResponse` (PascalCase + action)

**Functions:**
- Methods: `create_email()`, `get_email()` (snake_case)
- Async methods: `async def create_email()` (always async for DB operations)

### Code Style

**Imports:**
- Standard library first
- Third-party libraries second
- Local imports last
- Alphabetical within each group

**Docstrings:**
- All public methods must have docstrings
- Format: Google style docstrings
- Include parameter types and return types

**Type Hints:**
- MANDATORY for all functions
- Use `Optional[T]` for nullable types
- Use `list[T]`, `dict[K, V]` for collections

### Security Practices

- Never log sensitive data (passwords, tokens)
- Always validate user input
- Use parameterized queries (SQLAlchemy ORM handles this)
- Sanitize error messages before returning to client
```

### Project Architecture Briefing

**File:** `.claude/agent_briefings/project_architecture.md`

**Customize for your project:**

```markdown
# Project Architecture Briefing

## Overview
[Brief description of your project]

## Technology Stack

**Backend:**
- Language: [Python/TypeScript/etc.]
- Framework: [FastAPI/Flask/Express/etc.]
- Database: [PostgreSQL/MySQL/MongoDB/etc.]

**Frontend:**
- Framework: [React/Vue/Angular/etc.]
- Language: [TypeScript/JavaScript]
- State Management: [Redux/Zustand/etc.]

## Architecture Patterns

### Layered Architecture

```
┌─────────────────────────────┐
│      API Layer (Routes)     │  ← Thin wrappers
├─────────────────────────────┤
│    Business Logic (Services)│  ← Core logic here
├─────────────────────────────┤
│    Data Access (Models)     │  ← Database interaction
└─────────────────────────────┘
```

### Directory Structure

```
[Your actual project structure]
```

### Design Principles

1. **Single Responsibility:** Each module has one reason to change
2. **Dependency Injection:** Services receive dependencies via constructor
3. **Interface Segregation:** Small, focused interfaces
4. **Separation of Concerns:** Business logic separate from API layer

## Development Workflow

### Coding Standards
- [List your standards]

### Testing Strategy
- [Your testing approach]

### Deployment Process
- [Your deployment workflow]

## Common Patterns

[Document recurring patterns in your codebase]
```

### Adding Custom Domain Briefings

**Create briefings for other domains:**

**Frontend Briefing:**
```bash
# Create file
touch .claude/agent_briefings/frontend_implementation.md
```

**Example content:**
```markdown
---
domain: frontend
updated: 2025-10-19
applies_to: [implementation-agent-v1, build-fixer-agent-v1]
---

# Frontend Implementation Briefing

## Technology Stack
- Framework: React 18+
- Language: TypeScript 5+
- State: Zustand
- Styling: Tailwind CSS

## File Structure

```
src/frontend/
├── components/          # React components
│   ├── common/          # Shared components
│   └── features/        # Feature-specific components
├── hooks/               # Custom React hooks
├── stores/              # Zustand stores
└── types/               # TypeScript interfaces
```

## Coding Patterns

### Component Pattern

```typescript
// components/EmailList.tsx
import { useEmailStore } from '@/stores/emailStore';

interface EmailListProps {
  userId: string;
}

export const EmailList: React.FC<EmailListProps> = ({ userId }) => {
  const { emails, fetchEmails } = useEmailStore();

  useEffect(() => {
    fetchEmails(userId);
  }, [userId, fetchEmails]);

  return (
    <div className="email-list">
      {emails.map(email => (
        <EmailCard key={email.id} email={email} />
      ))}
    </div>
  );
};
```

[Continue with frontend-specific patterns...]
```

---

## 2. Customize Validation Scripts

Validation scripts define how code quality is enforced during Phase 2 of the workflow.

### Location

**File:** `package.json` (project root)

### Python Projects

**Basic Validation:**
```json
{
  "scripts": {
    "validate": "ruff check src/ && mypy src/"
  }
}
```

**With Testing:**
```json
{
  "scripts": {
    "lint": "ruff check src/",
    "type-check": "mypy src/",
    "test": "pytest tests/ --maxfail=1",
    "validate": "npm run lint && npm run type-check && npm run test"
  }
}
```

**With Coverage Requirements:**
```json
{
  "scripts": {
    "lint": "ruff check src/",
    "type-check": "mypy src/",
    "test": "pytest tests/ --cov=src --cov-fail-under=80",
    "validate": "npm run lint && npm run type-check && npm run test"
  }
}
```

### TypeScript Projects

**Basic Validation:**
```json
{
  "scripts": {
    "lint": "eslint src/ --ext .ts,.tsx",
    "type-check": "tsc --noEmit",
    "validate": "npm run lint && npm run type-check"
  }
}
```

**With Testing:**
```json
{
  "scripts": {
    "lint": "eslint src/ --ext .ts,.tsx",
    "type-check": "tsc --noEmit",
    "test": "jest --passWithNoTests",
    "validate": "npm run lint && npm run type-check && npm run test"
  }
}
```

**With Build Verification:**
```json
{
  "scripts": {
    "lint": "eslint src/ --ext .ts,.tsx",
    "type-check": "tsc --noEmit",
    "test": "jest --passWithNoTests",
    "build": "tsc && vite build",
    "validate": "npm run lint && npm run type-check && npm run test && npm run build"
  }
}
```

### Multi-Language Projects

**Python + TypeScript:**
```json
{
  "scripts": {
    "validate:backend": "ruff check src/backend/ && mypy src/backend/",
    "validate:frontend": "eslint src/frontend/ --ext .ts,.tsx && tsc --noEmit",
    "validate": "npm run validate:backend && npm run validate:frontend"
  }
}
```

### Configuration Files

**Ruff Configuration (`pyproject.toml`):**
```toml
[tool.ruff]
line-length = 100
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
]
ignore = [
    "E501",  # line-too-long (handled by formatter)
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**ESLint Configuration (`.eslintrc.json`):**
```json
{
  "parser": "@typescript-eslint/parser",
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn"
  }
}
```

---

## 3. Customize Commit Messages

Commit messages follow the Conventional Commits format. Customize the template to match your project's needs.

### Default Format

```
<type>(<epic-id>): <short description>

<body>

<metadata footer>
```

### Customization Options

#### 1. Change Commit Type

**Default types:**
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code refactoring
- `docs` - Documentation
- `test` - Testing
- `chore` - Maintenance

**Add custom types:**
```bash
# In workflow command, modify commit type detection:
if [[ "$SPEC" =~ "bug" || "$SPEC" =~ "fix" ]]; then
    COMMIT_TYPE="fix"
elif [[ "$SPEC" =~ "refactor" || "$SPEC" =~ "cleanup" ]]; then
    COMMIT_TYPE="refactor"
elif [[ "$SPEC" =~ "security" ]]; then
    COMMIT_TYPE="security"  # Custom type
else
    COMMIT_TYPE="feat"
fi
```

#### 2. Add Issue References

**GitHub Issues:**
```bash
# Get issue number from epic
ISSUE_NUMBER=$(grep "Issue:" "$EPIC_DIR/spec.md" | cut -d':' -f2 | tr -d ' ')

# Add to commit message
git commit -m "$(cat <<EOF
feat(EPIC-042): Add email validation

Implemented email format validation...

Closes #${ISSUE_NUMBER}

🤖 Generated with Claude Code
...
EOF
)"
```

**Jira Integration:**
```bash
# Get Jira ticket from epic
JIRA_TICKET=$(grep "Jira:" "$EPIC_DIR/spec.md" | cut -d':' -f2 | tr -d ' ')

# Add to commit message
git commit -m "$(cat <<EOF
feat(EPIC-042): Add email validation

Implemented email format validation...

Jira: ${JIRA_TICKET}

🤖 Generated with Claude Code
...
EOF
)"
```

#### 3. Customize Footer

**Remove Claude branding:**
```bash
git commit -m "$(cat <<EOF
feat(EPIC-042): Add email validation

Implemented email format validation...

Files:
- Created: 3 files
- Modified: 2 files

Automated implementation via workflow command.
EOF
)"
```

**Add team metadata:**
```bash
git commit -m "$(cat <<EOF
feat(EPIC-042): Add email validation

Implemented email format validation...

Files:
- Created: 3 files
- Modified: 2 files

Team: Backend
Sprint: Sprint-24
Reviewed-By: Automated workflow

🤖 Generated with Claude Code
https://claude.com/claude-code
EOF
)"
```

#### 4. Add Signed Commits

**GPG Signing:**
```bash
# Enable GPG signing
git config --global commit.gpgsign true

# Workflow will automatically sign commits
git commit -S -m "..."
```

---

## 4. Customize Parallel Detection

Parallel detection determines when to use parallel execution vs sequential. Adjust thresholds based on your project's needs.

### Default Thresholds

```bash
MIN_FILES=5              # Minimum files to consider parallel
MIN_DOMAINS=2            # Minimum domains required
MAX_OVERLAP=30           # Maximum file overlap percentage
```

### Customization

**Location:** Workflow command or parallel_detection.py script

#### Option 1: Adjust in Workflow Command

```bash
# In .claude/commands/execute-workflow.md

# More aggressive parallelization (lower bar)
PARALLEL_RESULT=$(python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  "$FILE_TASKS" \
  --min-files 3 \
  --min-domains 2 \
  --max-overlap 40)

# More conservative parallelization (higher bar)
PARALLEL_RESULT=$(python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  "$FILE_TASKS" \
  --min-files 10 \
  --min-domains 3 \
  --max-overlap 20)
```

#### Option 2: Project-Specific Config

**Create config file:**
```bash
# .workflow/parallel_config.json
{
  "min_files": 7,
  "min_domains": 2,
  "max_overlap_percentage": 25,
  "custom_domains": {
    "infrastructure": ["terraform/", "ansible/", "*.yml"],
    "mobile": ["src/mobile/", "*.swift", "*.kotlin"]
  }
}
```

**Use in workflow:**
```bash
PARALLEL_RESULT=$(python3 ~/tier1_workflow_global/implementation/parallel_detection.py \
  "$FILE_TASKS" \
  --config .workflow/parallel_config.json)
```

### Domain Classification

**Add custom domain patterns:**

Edit `parallel_detection.py`:

```python
DOMAIN_RULES = {
    # Existing domains
    "backend": [r"^src/backend/", r"^src/api/", r".*\.service\.py$"],
    "frontend": [r"^src/frontend/", r"^src/components/", r".*\.tsx$"],

    # Add custom domains
    "infrastructure": [r"^terraform/", r"^ansible/", r".*\.tf$", r".*\.yml$"],
    "mobile": [r"^src/mobile/", r".*\.swift$", r".*\.kotlin$"],
    "data": [r"^src/data/", r"^etl/", r".*_pipeline\.py$"],
}
```

---

## 5. Add Post-Mortem Analysis

Post-mortem analysis provides continuous improvement feedback after workflow execution.

### Enable Post-Mortem

**Location:** Workflow command Phase 5 (after commit)

**Add to workflow:**

```bash
# Phase 5: Commit & Cleanup
...
git commit -m "..."

# Optional: Deploy post-mortem agent
if [ "$ENABLE_POST_MORTEM" = "true" ]; then
    echo "📊 Running post-mortem analysis..."

    Task(
        subagent_type="general-purpose",
        description="Post-mortem analysis for EPIC-042",
        prompt="""
        $(cat ~/.claude/agent_definitions/post_mortem_agent_v1.md)

        EPIC ID: $EPIC_ID

        ARTIFACTS:
        - Implementation results: .workflow/outputs/$EPIC_ID/phase1_results.json
        - Validation results: .workflow/outputs/$EPIC_ID/validation_results.json

        Analyze workflow execution and provide recommendations.
        """
    )
fi
```

### Configuration

**Enable/disable via environment variable:**

```bash
# ~/.bashrc or project-specific .env
export ENABLE_POST_MORTEM=true   # Enable post-mortem
export ENABLE_POST_MORTEM=false  # Disable post-mortem
```

**Or per-epic:**

```bash
# Enable for this epic only
ENABLE_POST_MORTEM=true /execute-workflow EPIC-042
```

### Post-Mortem Output

**Location:** `.workflow/outputs/EPIC-042/post_mortem.md`

**Example output:**
```markdown
# Post-Mortem Analysis: EPIC-042

## Execution Summary
- Duration: 4m 12s
- Files created: 2
- Files modified: 3
- Validation attempts: 1 (passed first try)
- Issues encountered: 0

## What Went Well
1. Implementation plan was clear and specific
2. No validation errors (code quality high)
3. All files created/modified as expected

## Areas for Improvement
1. Type hints could be more explicit in email_validator.py
2. Consider adding docstrings to exception classes

## Recommendations

### For Future Epics
1. Include example usage in file-tasks.md
2. Specify error handling requirements explicitly

### For Agent Briefings
1. Add section on custom exception documentation
2. Include examples of RFC compliance patterns

### For Validation
1. Consider adding docstring linting (pydocstyle)
2. Add import ordering checks (isort)
```

---

## Summary

**Key Customizations:**

1. **Agent Briefings** - Update for your tech stack, file structure, and patterns
2. **Validation Scripts** - Define linting, type checking, testing requirements
3. **Commit Messages** - Customize format, add issue references, modify footer
4. **Parallel Detection** - Adjust thresholds and add custom domains
5. **Post-Mortem** - Enable continuous improvement feedback

**Recommended Order:**

1. Start with agent briefings (most important)
2. Add validation scripts (ensure code quality)
3. Customize commit messages (match team conventions)
4. Adjust parallel detection (optimize performance)
5. Add post-mortem (continuous improvement)

**Testing Customizations:**

1. Create small test epic (3-5 files)
2. Run workflow: `/execute-workflow EPIC-TEST`
3. Review results and refine customizations
4. Document project-specific patterns

---

## Next Steps

- Read [WORKFLOW_INTEGRATION_GUIDE.md](./WORKFLOW_INTEGRATION_GUIDE.md) for setup
- Read [WORKFLOW_EXAMPLE.md](./WORKFLOW_EXAMPLE.md) for complete walkthrough
- Read [WORKFLOW_TROUBLESHOOTING.md](./WORKFLOW_TROUBLESHOOTING.md) for issues

**Templates Available:**
- Agent briefings: `~/tier1_workflow_global/implementation/agent_briefings/`
- Agent definitions: `~/tier1_workflow_global/implementation/agent_definitions/`
- Parallel detection: `~/tier1_workflow_global/implementation/parallel_detection.py`
