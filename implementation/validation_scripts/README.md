# Validation Scripts - Customization Guide

**Purpose:** Template validation scripts for projects to customize based on their technology stack.

## Overview

These validation scripts are **copy-and-customize templates**. Each project should adapt them to match their specific:
- Programming languages (Python, TypeScript, Go, etc.)
- Build tools (npm, poetry, cargo, etc.)
- Linters (ruff, eslint, golangci-lint, etc.)
- Type checkers (mypy, TypeScript compiler, etc.)
- Test frameworks (pytest, jest, etc.)

**These scripts are NOT one-size-fits-all.** They provide patterns and structure that you adapt to your project.

## Validation Categories

### 1. Architecture Validation (Optional)

**File:** `validate_architecture.py`

**Purpose:** Enforce architectural boundaries (layered architecture, hexagonal architecture, etc.)

**Customize for:**
- Your project's layer structure (e.g., domain/application/infrastructure)
- Allowed/forbidden import patterns
- Boundary crossing rules

**Example use cases:**
- Domain layer should not import infrastructure layer
- Frontend components should not import backend code
- Shared utilities should not depend on feature-specific code

**Skip if:** Your project doesn't have strict architectural boundaries or layers.

---

### 2. Contract Validation (Optional)

**File:** `validate_contracts.py`

**Purpose:** Validate that code implementation matches specification contracts (API schemas, interfaces, etc.)

**Customize for:**
- OpenAPI/Swagger schema validation
- GraphQL schema validation
- gRPC proto validation
- TypeScript interface validation
- Python protocol/ABC validation

**Example use cases:**
- API endpoints match OpenAPI spec
- Database models match schema definitions
- Frontend types match backend API contracts

**Skip if:** Your project doesn't have formal contracts or schemas.

---

### 3. Build & Lint (Mandatory)

**Purpose:** Ensure code compiles and follows style guidelines

**Python example:**
```bash
# Linting
ruff check .
ruff check --fix .  # Auto-fix

# Formatting
ruff format --check .
ruff format .  # Auto-format

# Type checking
mypy src/ --strict
```

**TypeScript example:**
```bash
# Build
tsc --noEmit

# Linting
eslint src/

# Formatting
prettier --check src/
```

**Go example:**
```bash
# Build
go build ./...

# Linting
golangci-lint run

# Formatting
gofmt -l .
```

---

## Integration with package.json Scripts

Even if your project uses Python, you can define validation commands in `package.json` for consistency:

```json
{
  "name": "my-python-project",
  "scripts": {
    "lint:py": "ruff check .",
    "lint:py:fix": "ruff check --fix .",
    "format:py": "ruff format .",
    "format:py:check": "ruff format --check .",
    "typecheck:py": "mypy src/ --strict",
    "test:py": "pytest tests/ -v",
    "validate-architecture": "python3 tools/validate_architecture.py",
    "validate-contracts": "python3 tools/validate_contracts.py",
    "validate-all": "npm run lint:py && npm run format:py:check && npm run typecheck:py && npm run validate-architecture && npm run validate-contracts"
  }
}
```

**Benefits:**
- Consistent command interface across projects
- Easy to run from workflow orchestrator
- Clear documentation of available validations

---

## Integration with Workflow (Phase 3)

The workflow orchestrator calls validation in **Phase 3** (after implementation):

```bash
# Phase 3: Validation
npm run validate-all

# If validation fails:
# → Deploy build_fixer_agent_v1
# → Retry validation (max 3 attempts)
```

See: `template/.claude/commands/execute-workflow.md` (Phase 3 section)

---

## Customization Steps

### Step 1: Copy Templates to Your Project

```bash
# Copy validation scripts to your project
cp -r ~/tier1_workflow_global/implementation/validation_scripts/ ./tools/

# Or create your own from scratch using these as reference
```

### Step 2: Customize for Your Stack

Edit each validation script to match your project:

1. **Update imports** - Use your project's modules
2. **Update file paths** - Match your project structure
3. **Update validation logic** - Enforce your architectural rules
4. **Update dependencies** - Install required validation tools

### Step 3: Add npm Scripts

Update your `package.json` with project-specific validation commands.

### Step 4: Test Validation Scripts

```bash
# Run each validation individually
npm run lint:py
npm run typecheck:py
npm run validate-architecture

# Run all validations
npm run validate-all
```

### Step 5: Integrate with Workflow

The workflow orchestrator will automatically use `npm run validate-all` in Phase 3.

---

## Example: Python Project

**Directory structure:**
```
my-project/
├── src/
│   ├── domain/        # Core business logic
│   ├── application/   # Use cases
│   └── infrastructure/  # External dependencies
├── tests/
├── tools/
│   ├── validate_architecture.py  # Customized for this project
│   └── validate_contracts.py     # Customized for this project
├── package.json       # Validation scripts
├── pyproject.toml     # Python config (ruff, mypy)
└── ruff.toml          # Ruff configuration
```

**package.json:**
```json
{
  "name": "my-python-project",
  "scripts": {
    "lint:py": "ruff check .",
    "lint:py:fix": "ruff check --fix .",
    "format:py": "ruff format .",
    "format:py:check": "ruff format --check .",
    "typecheck:py": "mypy src/ --strict",
    "test:py": "pytest tests/ -v --cov=src",
    "validate-architecture": "python3 tools/validate_architecture.py",
    "validate-all": "npm run lint:py && npm run format:py:check && npm run typecheck:py && npm run validate-architecture"
  }
}
```

---

## Example: TypeScript Project

**package.json:**
```json
{
  "name": "my-typescript-project",
  "scripts": {
    "build:ts": "tsc --noEmit",
    "lint:ts": "eslint src/ --ext .ts,.tsx",
    "lint:ts:fix": "eslint src/ --ext .ts,.tsx --fix",
    "format:ts": "prettier --write src/",
    "format:ts:check": "prettier --check src/",
    "test:ts": "jest",
    "validate-architecture": "ts-node tools/validate_architecture.ts",
    "validate-all": "npm run build:ts && npm run lint:ts && npm run format:ts:check && npm run validate-architecture"
  }
}
```

---

## Example: Polyglot Project (Python + TypeScript)

**package.json:**
```json
{
  "name": "my-fullstack-project",
  "scripts": {
    "lint:py": "ruff check backend/",
    "lint:ts": "eslint frontend/src/ --ext .ts,.tsx",
    "typecheck:py": "mypy backend/src/ --strict",
    "typecheck:ts": "tsc -p frontend/tsconfig.json --noEmit",
    "format:py": "ruff format backend/",
    "format:ts": "prettier --write frontend/src/",
    "test:py": "pytest backend/tests/",
    "test:ts": "jest frontend/",
    "validate-architecture": "python3 tools/validate_architecture.py",
    "validate-all": "npm run lint:py && npm run lint:ts && npm run typecheck:py && npm run typecheck:ts && npm run validate-architecture"
  }
}
```

---

## Validation Script Examples

### Architecture Validator (Python)

**Purpose:** Ensure domain layer doesn't import infrastructure

```python
#!/usr/bin/env python3
"""Validate architectural boundaries."""

import sys
from pathlib import Path
import re

def check_architecture_boundaries():
    """Check that domain layer doesn't import infrastructure."""
    violations = []

    domain_files = Path("src/domain").rglob("*.py")

    for file_path in domain_files:
        content = file_path.read_text()

        # Check for infrastructure imports
        infra_imports = re.findall(
            r'from\s+(?:src\.)?infrastructure\.|import\s+(?:src\.)?infrastructure',
            content
        )

        if infra_imports:
            violations.append({
                "file": str(file_path),
                "violation": "Domain layer imports infrastructure layer",
                "imports": infra_imports
            })

    if violations:
        print("❌ Architecture violations detected:")
        for v in violations:
            print(f"  File: {v['file']}")
            print(f"  Issue: {v['violation']}")
            print(f"  Imports: {v['imports']}")
        sys.exit(1)
    else:
        print("✅ Architecture validation passed")
        sys.exit(0)

if __name__ == "__main__":
    check_architecture_boundaries()
```

### Contract Validator (Python + OpenAPI)

**Purpose:** Ensure API endpoints match OpenAPI spec

```python
#!/usr/bin/env python3
"""Validate API endpoints match OpenAPI spec."""

import sys
from pathlib import Path
import yaml
import re

def check_api_contracts():
    """Check that API endpoints match OpenAPI spec."""
    violations = []

    # Load OpenAPI spec
    spec_path = Path("api/openapi.yaml")
    if not spec_path.exists():
        print("ℹ️ No OpenAPI spec found - skipping contract validation")
        sys.exit(0)

    spec = yaml.safe_load(spec_path.read_text())
    spec_endpoints = set(spec.get("paths", {}).keys())

    # Extract endpoints from code
    api_files = Path("src/api").rglob("*.py")
    code_endpoints = set()

    for file_path in api_files:
        content = file_path.read_text()

        # Extract Flask/FastAPI routes
        routes = re.findall(r'@app\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']', content)
        code_endpoints.update(routes)

    # Check for mismatches
    missing_in_code = spec_endpoints - code_endpoints
    missing_in_spec = code_endpoints - spec_endpoints

    if missing_in_code:
        violations.append(f"Endpoints in spec but not in code: {missing_in_code}")

    if missing_in_spec:
        violations.append(f"Endpoints in code but not in spec: {missing_in_spec}")

    if violations:
        print("❌ Contract violations detected:")
        for v in violations:
            print(f"  {v}")
        sys.exit(1)
    else:
        print("✅ Contract validation passed")
        sys.exit(0)

if __name__ == "__main__":
    check_api_contracts()
```

---

## Non-Blocking Failures

**Important:** Validation is **optional** and **non-blocking** in the workflow.

If validation fails:
1. Build fixer agent is deployed (up to 3 attempts)
2. If still failing after 3 attempts → Workflow continues anyway
3. Manual intervention suggested but not required

**Why non-blocking?**
- Projects may not have all validations configured yet
- Early-stage projects may intentionally skip some checks
- Allows workflow to complete even with validation issues

**To make validation blocking:**
Update `execute-workflow.md` Phase 3 to `exit 1` on failure instead of continuing.

---

## Testing Your Validation Setup

### Test 1: Validation Passes

```bash
# Make sure code is clean
npm run lint:py:fix
npm run format:py

# Run validation
npm run validate-all

# Expected: All checks pass ✅
```

### Test 2: Validation Fails

```bash
# Introduce a linting error
echo "import os  # unused import" >> src/test.py

# Run validation
npm run validate-all

# Expected: Linting fails ❌
# Expected: Build fixer agent would be deployed
```

### Test 3: Auto-Fix

```bash
# Run auto-fix
npm run lint:py:fix

# Run validation again
npm run validate-all

# Expected: All checks pass ✅
```

---

## Summary

**Key Points:**
1. **Templates, not solutions** - Customize for your project
2. **Optional validations** - Architecture/contract validation are optional
3. **Mandatory validations** - Build/lint/typecheck are recommended
4. **npm scripts for consistency** - Works across Python/TypeScript/other languages
5. **Non-blocking failures** - Workflow continues even if validation fails
6. **Build fixer agent** - Automatically attempts to fix validation errors

**Next Steps:**
1. Copy templates to your project (`tools/` directory)
2. Customize validation logic for your stack
3. Add npm scripts to `package.json`
4. Test validation commands
5. Integrate with workflow (Phase 3)

**Need Help?**
- See `VALIDATION_SYSTEM.md` for architecture details
- See `VALIDATION_RETRY_WORKFLOW.md` for retry loop details
- See test cases in `implementation/test_cases/validation_*.md`
