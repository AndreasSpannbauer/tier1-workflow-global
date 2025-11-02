## Mandatory Pre-Specification Analysis

**BEFORE writing any specification, you MUST complete this research workflow:**

This ensures all specifications leverage existing patterns and up-to-date library documentation, following the **Pattern Library → Context7 fallback** workflow.

---

### Research Workflow (MANDATORY FOR ALL SPECS)

**Purpose:** Ensure specifications leverage existing patterns and up-to-date library documentation.

#### Step 1: Identify External Dependencies

Analyze the user's requirements to identify ALL external libraries, frameworks, and APIs:

**Explicitly mentioned:**
- Direct library names (e.g., "use FastAPI", "integrate with Stripe API")
- Specific frameworks (e.g., "React frontend", "PostgreSQL database")
- Third-party services (e.g., "Twilio for SMS", "Ollama for LLM")

**Implicitly required:**
- "Real-time WebSockets" → likely Socket.IO or similar
- "GPU transcription" → likely Whisper
- "Authentication with JWT" → library-specific JWT implementation
- "Async task processing" → likely Celery, RabbitMQ, or similar

**Infrastructure dependencies:**
- Databases (PostgreSQL, MongoDB, Redis)
- Message queues (RabbitMQ, Kafka)
- Container orchestration (Docker, Kubernetes)
- Cloud services (AWS, GCP, Azure)

**Create list:** Document all detected dependencies for research.

---

#### Step 2: For EACH Dependency, Follow This Workflow

##### 2a. Pattern Library Search (FIRST - ALWAYS - Baseline)

**Use the MCP pattern library to search for existing curated patterns as your starting point:**

```python
# Search pattern library with context
mcp__pattern-library__search_patterns(
    query="<library-name> <specific-use-case>",
    mode="auto",  # Tries keyword first, falls back to semantic
    top_k=5
)
```

**Example queries:**
- `"FastAPI user authentication JWT"`
- `"Whisper transcription integration remote server"`
- `"SQLAlchemy repository pattern async"`
- `"React state management complex forms"`
- `"PostgreSQL connection pooling async"`
- `"Celery task retry exponential backoff"`

**Retrieve and evaluate patterns:**

**If patterns found:**
1. Retrieve pattern(s):
   ```python
   mcp__pattern-library__retrieve_pattern(pattern_id="<pattern-id>")
   ```
2. Review pattern content
3. Save to `.tasks/backlog/EPIC-XXX/research/<library>-patterns.md`
4. **Evaluate:** Are these patterns sufficient for THIS specific use case?

**Decision criteria (USE YOUR JUDGMENT):**

✅ **Patterns are sufficient IF:**
- Patterns directly address this use case
- Patterns are recent/current (not outdated)
- Patterns cover the specific integration/features needed
- You're confident in the approach

❌ **Supplement with Context7 IF (even if patterns exist):**
- Patterns are outdated or incomplete
- This use case has unique requirements not covered
- Library has had major version changes since patterns created
- You need verification or more specific details
- **You have ANY doubt about pattern applicability**

**Important:** Patterns provide a **baseline**, not a constraint. You're **encouraged** to call Context7 when it would improve quality, even if patterns exist.

---

##### 2b. Context7 Research (Supplement or Fallback)

**Call Context7 when:**
- No patterns found in pattern library, OR
- Patterns exist but are insufficient/outdated for this use case, OR
- You need fresh documentation to verify or supplement patterns

**Use Context7 to fetch fresh library documentation:**

**Step 1: Resolve library ID**

```python
# Resolve library name to Context7-compatible ID
mcp__context7__resolve-library-id(libraryName="<library-name>")

# Returns list of matching libraries
# Choose most relevant match (usually first result)
```

**Step 2: Get focused documentation**

```python
# Fetch documentation focused on specific use case
mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/org/project",  # From Step 1
    topic="<specific-topic>",  # e.g., "authentication", "async workers"
    tokens=5000  # Adjust based on complexity
)
```

**Topic examples:**
- "authentication and authorization"
- "database connection pooling"
- "WebSocket real-time communication"
- "background task processing"
- "API integration patterns"

**Save documentation:**
1. Write to `.tasks/backlog/EPIC-XXX/research/<library>-context7.md`
2. Include metadata:
   - Library ID
   - Topic searched
   - Retrieval date
3. **Auto-queued for extraction** (PostToolUse hook captures Context7 calls)
4. Extract later with `/extract-patterns` to improve pattern library

**Accept results and continue** (fresh documentation acquired)

---

##### 2c. Document Research (MANDATORY)

**Create comprehensive research summary:**

`.tasks/backlog/EPIC-XXX/research/README.md`:

```markdown
# Research Summary for EPIC-XXX

**Epic Title:** <epic-title>
**Created:** <date>

## External Dependencies Researched

### <Library 1>
- **Source:** Pattern Library / Context7
- **Patterns Used:** <pattern-ids> / "Fresh Context7 docs"
- **Key Integration Points:**
  - <Integration point 1>
  - <Integration point 2>
- **Saved To:** `<library>-patterns.md` / `<library>-context7.md`
- **Notes:** <Any special considerations>

### <Library 2>
...

## No External Dependencies

_Check this if using only built-in functionality:_

- [ ] Confirmed: No external libraries required
- [ ] Justification: Using standard library/built-in features only

## Research Impact on Specification

**Patterns applied:**
- <Pattern 1>: Influences <architecture decision>
- <Pattern 2>: Defines <data model approach>

**Documentation insights:**
- <Library X>: <Key insight affecting design>
- <Library Y>: <Best practice to follow>

## Next Steps

- [ ] Review all research documents
- [ ] Apply patterns to architecture design
- [ ] Define contracts based on library patterns
- [ ] Extract Context7 docs to pattern library (`/extract-patterns`)
```

---

### Skip Conditions (RARE)

**Research is MANDATORY unless ALL of the following are true:**

1. ✅ No external libraries detected (built-in functionality only)
2. ✅ User explicitly confirms no external dependencies
3. ✅ Specification is purely organizational (no code changes)
4. ✅ No third-party APIs or services involved

**If ANY external library, framework, or service is used, research is MANDATORY.**

---

### Why This Workflow Matters

#### Pattern Library First (Efficiency via Reuse)

**Start with what we already know:**
- **Curated expertise:** Proven implementations from past successful projects
- **Consistency:** Ensures similar problems solved using similar approaches
- **Speed:** Local semantic search via Ollama GPU (<20ms latency)
- **Usage-boosted ranking:** Frequently-used patterns ranked higher
- **Context-aware:** Patterns include full implementation context

**Saves 5-15k tokens per library** when patterns are sufficient.

**Pattern library location:** `~/.claude/pattern_library/patterns/`

**Current coverage:** GPU compute, Ollama, Whisper, SSH, Context7, FastAPI, SQLAlchemy, React, and growing...

#### Context7 Supplement (Quality via Fresh Docs)

**When pattern library isn't enough, supplement with Context7:**

**Use Context7 to:**
- **Verify:** Check if patterns are still current/best practice
- **Supplement:** Add library-specific details not in patterns
- **Update:** Get latest API changes or version-specific info
- **Specialize:** Address edge cases unique to your use case

**Benefits:**
- **Up-to-date:** Latest library documentation and API references
- **Comprehensive:** 5k tokens focused on specific use case
- **Self-improving:** Auto-queued for extraction → grows pattern library
- **Quality assurance:** Never be constrained by outdated patterns

**Auto-capture workflow:**
1. Context7 call → PostToolUse hook captures output
2. Saved to `~/.claude/pattern_library/extraction_queue/`
3. Run `/extract-patterns` → Claude extracts reusable patterns
4. Patterns added to `~/.claude/pattern_library/patterns/`
5. Index rebuilt → Future specs auto-inject patterns

#### Continuous Improvement Loop

```
User creates spec
    ↓
Pattern library search (ALWAYS - baseline)
    ↓
    ├─ Patterns sufficient → Use patterns ✅
    │
    ├─ Patterns exist but insufficient → Use patterns + Context7 ✅✅
    │                                    (Best of both)
    │
    └─ No patterns → Context7 only
                      ↓
                  Save docs + Auto-queue
                      ↓
                  /extract-patterns
                      ↓
                  New patterns → Pattern library
                      ↓
                  Future specs: patterns + optional Context7 ✨
```

**Philosophy:**
- **Efficiency:** Start with patterns (fast, consistent)
- **Quality:** Supplement with Context7 when needed (fresh, specific)
- **Growth:** Every Context7 call improves pattern library
- **Judgment:** You decide when Context7 adds value

**Result:** Pattern library grows over time, reducing (but not eliminating) Context7 dependency. Context7 remains available for verification, updates, and specialization.

---

### Integration with Specification Process

**After completing research:**

1. **Architecture Design (Phase 3):**
   - Apply patterns from pattern library
   - Use Context7 docs for library-specific decisions
   - Reference research files in architecture.md

2. **YAML Contract Generation (Phase 4):**
   - Use library patterns for contract structures
   - Follow API conventions from documentation
   - Ensure compatibility with library schemas

3. **Implementation Planning (Phase 5):**
   - Reference patterns in file-tasks.md
   - Include library-specific setup steps
   - Plan integration testing based on research

**Research artifacts used throughout specification:**
- `research/README.md` → Overview of dependencies
- `research/<library>-patterns.md` → Curated implementation patterns
- `research/<library>-context7.md` → Fresh library documentation

---

### Validation Checklist

**Before proceeding to architecture design, verify:**

- [ ] All external dependencies identified
- [ ] Each dependency researched (pattern library OR Context7)
- [ ] Research results saved to `.tasks/backlog/EPIC-XXX/research/`
- [ ] `research/README.md` created with summary
- [ ] Patterns retrieved and reviewed (if applicable)
- [ ] Context7 docs saved and queued for extraction (if used)
- [ ] Research insights documented for architecture phase

**Research gate:** Specification cannot proceed without completing research for all identified dependencies.

---
