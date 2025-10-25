# Project Constitution - Tier1 Workflow

**Version:** 1.0
**Effective Date:** 2025-10-25
**Philosophy:** Simplicity, pragmatism, real implementations
**Enforcement:** Warnings except Article III (simulation detection blocks)

---

## Purpose

This constitution establishes architectural principles for Tier1 workflow projects. All implementations should comply with these principles. Violations generate warnings; only Article III (simulation code) blocks commits.

**Enforcement:** Pre-commit hook validates compliance. Warnings can be overridden with justification.

---

## Article I: Simplicity Imperative

**Principle:** Keep it simple. No speculative features.

### Rules
1. Remove dead code immediately
2. No "we might need this later" implementations
3. YAGNI (You Aren't Gonna Need It)
4. Focus on current requirements only

### Validation
- Manual code review (subjective)
- Severity: Warning

### Examples

✅ **Good:**
```python
def process_email(email: str) -> str:
    """Process email with current requirements only."""
    return email.strip().lower()
```

❌ **Bad:**
```python
def process_email(email: str, future_options: dict = None) -> str:
    """Process email with future flexibility we might need."""
    # Added 10 options we don't use yet "just in case"
    if future_options:  # Never called
        pass
    return email.strip().lower()
```

---

## Article II: Anti-Abstraction Principle

**Principle:** Use framework features directly. Avoid unnecessary wrappers.

### Rules
1. No custom wrappers around framework features without specific need
2. Use framework idioms (FastAPI, React, SQLAlchemy, etc.)
3. Single model representation per entity (no redundant DTOs)
4. Document justification when abstraction IS required

### Allowed Abstractions
- Security concerns (input sanitization, authentication)
- Framework migration in progress (with timeline)
- Multi-framework support (documented requirement)

### Validation
- `tools/validate_constitutional_compliance.py` (AST-based heuristic)
- Severity: Warning

### Escape Hatch
```python
# tier1-constitution-ignore: article-ii
class MyWrapper:
    """Justified abstraction - see ADR-123"""
    pass
```

### Examples

✅ **Good:**
```python
# Direct FastAPI usage
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/analyze")
async def analyze(request: AnalysisRequest):
    return await service.analyze(request)
```

❌ **Bad:**
```python
# Unnecessary wrapper around FastAPI
class RequestHandler:
    """Custom wrapper around FastAPI (why?)"""

    def handle_post(self, path: str, handler):
        @app.post(path)
        async def wrapper(request):
            return await handler(request)
        return wrapper

# Usage: handler.handle_post("/api/analyze", analyze_func)
# Why? FastAPI already provides this with @app.post!
```

✅ **Good:**
```python
# Single model with Pydantic
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
```

❌ **Bad:**
```python
# Redundant models for same entity
class User(BaseModel):
    id: int
    name: str

class UserDTO(BaseModel):
    id: int
    name: str

class UserResponse(BaseModel):
    id: int
    name: str

class UserModel(BaseModel):
    id: int
    name: str

# Four models for the same thing!
```

---

## Article III: No Simulation Code (Agent Failure Protocol)

**Principle:** Real implementations only. No mocks, stubs, or placeholders in source code.

### Rules
1. **ZERO TOLERANCE** for simulation patterns in source code
2. Agents MUST report blockers instead of improvising fake implementations
3. Test mocks allowed ONLY in test files (with clear markers like `@pytest.fixture`)
4. No keyword-based conditional returns (if "test" in input: return "fake_response")

### Validation
- `tools/detect_simulation_code.py` (automated AST + regex detection)
- Severity: **ERROR (BLOCKS COMMIT)**

### Examples

✅ **Good:**
```python
def analyze_sentiment(text: str) -> SentimentResult:
    """Real implementation using actual ML model."""
    model = load_model("sentiment_analyzer.pkl")
    scores = model.predict([text])[0]
    return SentimentResult(
        positive=scores[0],
        negative=scores[1],
        neutral=scores[2]
    )
```

❌ **Bad:**
```python
def analyze_sentiment(text: str) -> SentimentResult:
    """Simulated implementation - TODO: Replace with real model."""
    # Keyword-based fake responses
    if "happy" in text.lower():
        return SentimentResult(positive=0.9, negative=0.1, neutral=0.0)
    elif "sad" in text.lower():
        return SentimentResult(positive=0.1, negative=0.9, neutral=0.0)
    else:
        return SentimentResult(positive=0.3, negative=0.3, neutral=0.4)
```

✅ **Good (test file):**
```python
# tests/test_sentiment.py
import pytest

@pytest.fixture
def mock_model():
    """Explicitly marked test fixture."""
    return MockSentimentModel()

def test_analyze_sentiment(mock_model):
    """Test with clearly marked mock."""
    result = analyze_sentiment("happy", model=mock_model)
    assert result.positive > 0.5
```

---

## Article IV: Contract-First (When Applicable)

**Principle:** If building MCP tools or REST APIs, contracts are mandatory.

### Rules
1. MCP tools → JSON Schema contracts in `contracts/mcp/`
2. REST APIs → OpenAPI specs or Pydantic models
3. GraphQL → SDL schemas
4. Contracts versioned and maintained

### When Required
- Implementing MCP tools/servers
- Building REST APIs
- Creating GraphQL endpoints
- Defining service interfaces

### When NOT Required
- Simple scripts or utilities
- Internal functions (not APIs)
- Prototypes (document intent to add later)

### Validation
- `tools/validate_contracts.py` (checks for contract files)
- Severity: Warning

### Examples

✅ **Good (MCP tool):**
```
contracts/mcp/tools/analyze_sentiment/
├── params.schema.json
├── result_success.schema.json
└── result_error.schema.json
```

✅ **Good (REST API):**
```python
from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    text: str
    options: dict = {}

class AnalysisResponse(BaseModel):
    sentiment: str
    confidence: float

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    ...
```

❌ **Bad:**
```python
@app.post("/api/analyze")
async def analyze(data: dict):
    # What fields are in data? What's returned? Nobody knows!
    result = process(data)
    return result
```

---

## Article V: Integration-First Testing (When Applicable)

**Principle:** Prefer integration tests over mocks when feasible.

### Rules
1. Use real databases (SQLite for tests, Docker containers for complex cases)
2. Use real services when possible
3. Mocking allowed for: external paid APIs, rate-limited services, hardware
4. Document exceptions with comments

### Philosophy
"Keep tests minimal" - Tier1 doesn't require comprehensive coverage, but the tests that exist should be realistic.

### Validation
- Manual code review
- Severity: Warning

### Examples

✅ **Good:**
```python
def test_email_processing(tmp_path):
    """Integration test with real SQLite database."""
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")

    # Real database, real processing
    with Session(engine) as session:
        result = process_email(email, session)
        assert result.status == "processed"
```

❌ **Bad:**
```python
def test_email_processing():
    """Test with mocked everything."""
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_service = MagicMock()

    # Not testing real behavior, just mocks
    result = process_email(email, mock_session, mock_service, mock_db)
    mock_service.process.assert_called_once()
```

✅ **Acceptable (documented exception):**
```python
def test_openai_integration():
    """Test OpenAI integration.

    Note: Using mock due to API costs ($0.01 per call).
    Integration verified manually and in staging environment.
    """
    with patch('openai.ChatCompletion.create') as mock_openai:
        mock_openai.return_value = {...}
        result = call_openai_api(prompt)
        assert result.success
```

---

## Article VI: Observable Systems

**Principle:** All functionality accessible via CLI with structured I/O.

### Rules
1. All services/modules expose CLI interfaces
2. CLI accepts text/JSON input (stdin, args, or files)
3. CLI produces text/JSON output (stdout)
4. Logs structured (JSON) for parsing
5. Errors include actionable remediation steps

### Benefits
- Easy testing: `python module.py < input.json > output.json`
- Automation friendly
- Debugging without full stack
- Self-documenting interfaces

### Validation
- `tools/validate_constitutional_compliance.py` (checks for CLI patterns)
- Severity: Warning

### CLI Standard Pattern

```python
import click
import json
import sys

@click.command()
@click.option('--input', type=click.File('r'), default=sys.stdin, help='Input file (or stdin)')
@click.option('--output', type=click.File('w'), default=sys.stdout, help='Output file (or stdout)')
@click.option('--format', type=click.Choice(['json', 'text']), default='json', help='Output format')
def process(input, output, format):
    """Process data with structured I/O."""
    # Read input
    if format == 'json':
        data = json.load(input)
    else:
        data = input.read()

    # Process
    result = service.process(data)

    # Write output
    if format == 'json':
        json.dump(result, output, indent=2)
    else:
        output.write(str(result))

if __name__ == '__main__':
    process()
```

### Examples

✅ **Good:**
```python
# src/sentiment_analyzer.py
import click

@click.command()
@click.argument('text', required=False)
@click.option('--file', type=click.File('r'), help='Read from file')
def analyze(text, file):
    """Analyze sentiment of text."""
    if file:
        text = file.read()

    result = SentimentAnalyzer().analyze(text)
    print(json.dumps(result.dict(), indent=2))

if __name__ == '__main__':
    analyze()

# Usage:
# python sentiment_analyzer.py "I am happy"
# python sentiment_analyzer.py --file email.txt
# echo "Great day!" | python sentiment_analyzer.py
```

✅ **Good (simpler):**
```python
# src/email_processor.py

def process_email(data: dict) -> dict:
    """Process email data."""
    # ... business logic ...
    return result

if __name__ == '__main__':
    import json
    import sys

    # Simple CLI: read JSON from stdin, write to stdout
    data = json.load(sys.stdin)
    result = process_email(data)
    json.dump(result, sys.stdout, indent=2)

# Usage:
# cat email.json | python email_processor.py > result.json
```

❌ **Bad:**
```python
# src/email_processor.py

def process_email(data: dict) -> dict:
    """Process email data."""
    # ... business logic ...
    return result

# No CLI interface - can only be called from other Python code
# Can't test without importing and running programmatically
```

---

## Enforcement Mechanisms

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Running Tier1 constitutional validation..."

# CRITICAL: Detect simulation code (BLOCKS)
python3 tools/detect_simulation_code.py src/ || exit 1

# OPTIONAL: Other constitutional checks (WARNS)
if [ -f "tools/validate_constitutional_compliance.py" ]; then
    python3 tools/validate_constitutional_compliance.py || true  # Don't block
fi

echo "✅ Validation complete"
```

### Escape Hatch for Warnings

Override warnings with justification comment:

```python
# tier1-constitution-ignore: article-ii
class MyWrapper:
    """
    Justified abstraction for X reason.
    See ADR-123 for detailed rationale.
    """
    pass
```

### Strict Mode (Optional)

Enable in `.tier1_config.json` to convert warnings to errors:

```json
{
  "constitutional_strict_mode": true,
  "constitutional_articles_enforced": ["I", "II", "III", "IV", "V", "VI"]
}
```

---

## Quick Reference Card

### Before Starting Implementation
- [ ] Read relevant constitutional articles
- [ ] Understand current requirements (Article I: no speculation)
- [ ] Check if contracts needed (Article IV: MCP/APIs)
- [ ] Plan CLI interface (Article VI: observability)

### During Implementation
- [ ] Use frameworks directly (Article II: no wrappers)
- [ ] Real implementations only (Article III: no simulation)
- [ ] Prefer integration tests (Article V: realistic tests)
- [ ] Add CLI interface (Article VI: `if __name__ == '__main__'`)

### Before Committing
- [ ] Remove any simulation code (Article III: BLOCKS)
- [ ] Remove unnecessary abstractions (Article II: warning)
- [ ] Ensure CLI exists (Article VI: warning)
- [ ] Contracts defined if needed (Article IV: warning)

---

**This constitution is a living document. Propose amendments when project needs evolve.**
