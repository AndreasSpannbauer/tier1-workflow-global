## Research External Libraries (MANDATORY)

**CRITICAL:** Query pattern library and Context7 for external dependencies BEFORE designing architecture.

This step ensures all specifications leverage:
- Existing curated patterns from the pattern library
- Up-to-date library documentation from Context7
- Proven integration approaches
- Consistent implementation patterns across projects

### Identify External Dependencies

Analyze user's answers from Rounds 1-3 to extract library/framework dependencies:

```bash
echo ""
echo "🔍 Analyzing external dependencies..."
echo ""

python3 << 'EOF'
import re
import sys

# Get answers from previous rounds
integrations = """${existing_components}"""
new_components = """${new_components}"""
data_sources = """${data_sources}"""

# Common libraries and frameworks to detect
known_libs = [
    "FastAPI", "Django", "Flask", "Express", "React", "Vue", "Angular",
    "SQLAlchemy", "Prisma", "TypeORM", "Sequelize",
    "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "Whisper", "Ollama", "OpenAI", "Anthropic",
    "Docker", "Kubernetes", "Terraform",
    "Pytest", "Jest", "Mocha", "Vitest",
    "NumPy", "Pandas", "SciPy", "Matplotlib",
    "TensorFlow", "PyTorch", "JAX",
    "Celery", "RabbitMQ", "Kafka",
    "Stripe", "Twilio", "SendGrid",
    "Socket.IO", "WebSocket", "gRPC", "GraphQL"
]

# Combine all answers
all_text = f"{integrations}\n{new_components}\n{data_sources}"

# Detect mentioned libraries
libraries_mentioned = []
for lib in known_libs:
    # Case-insensitive regex word boundary match
    if re.search(rf'\b{lib}\b', all_text, re.IGNORECASE):
        libraries_mentioned.append(lib)

# Remove duplicates and sort
libraries_mentioned = sorted(set(libraries_mentioned))

if libraries_mentioned:
    print("📦 Detected external dependencies:")
    for lib in libraries_mentioned:
        print(f"  - {lib}")
    print("")

    # Export for later use
    import os
    os.environ["DETECTED_LIBRARIES"] = ",".join(libraries_mentioned)
else:
    print("ℹ️  No external libraries auto-detected")
    print("   If your implementation uses external libraries, list them manually.")
    print("")

EOF

# Store detected libraries
DETECTED_LIBRARIES="${DETECTED_LIBRARIES:-}"

if [ -z "$DETECTED_LIBRARIES" ]; then
    echo "**User confirmation required:**"
    echo "  Does this epic use any external libraries or frameworks?"
    echo "  If yes, please list them (comma-separated):"
    echo ""
    echo "  Examples:"
    echo "    - FastAPI, SQLAlchemy, Pydantic"
    echo "    - React, TypeScript, Tailwind CSS"
    echo "    - Whisper, Ollama (for GPU/AI workloads)"
    echo ""

    # Wait for user input
    # (In actual execution, this would be an interactive prompt)
    # For now, store empty and let user manually trigger research
fi

echo ""
```

**Store detected libraries in:** `DETECTED_LIBRARIES` variable (comma-separated)

---

### Research Workflow (For EACH detected library)

**MANDATORY:** For each library in `DETECTED_LIBRARIES`, follow this workflow:

#### Step 1: Pattern Library Search (ALWAYS FIRST - Baseline)

Use the MCP pattern library to search for existing curated patterns as your **starting point**:

```python
# For each library, search pattern library
for library in DETECTED_LIBRARIES.split(','):
    library = library.strip()

    # Construct search query with context
    use_case = "integration"  # Extract from user answers if possible
    query = f"{library} {use_case}"

    print(f"\n🔍 Searching pattern library for: {library}")
    print(f"   Query: {query}")

    # Use MCP tool
    results = mcp__pattern-library__search_patterns(
        query=query,
        mode="auto",  # Tries keyword first, falls back to semantic
        top_k=5
    )

    # Evaluate results
    if results and len(results) >= 1:
        print(f"   ✅ Found {len(results)} pattern(s)")

        # Retrieve top patterns
        for pattern in results[:3]:  # Top 3
            pattern_content = mcp__pattern-library__retrieve_pattern(
                pattern_id=pattern['id']
            )

            # Save to research directory
            pattern_file = f"${EPIC_DIR}/research/{library.lower()}-patterns.md"
            with open(pattern_file, 'a') as f:
                f.write(f"\n\n## Pattern: {pattern['id']}\n\n")
                f.write(pattern_content)
                f.write("\n\n---\n")

        print(f"   📄 Saved to: research/{library.lower()}-patterns.md")
        print(f"   📋 Patterns retrieved as baseline")

        # IMPORTANT: Don't automatically skip Context7
        # Continue to Step 2 evaluation
    else:
        print(f"   ⚠️  No relevant patterns found")
        print(f"   → Will need Context7 research")
```

**Evaluation criteria (USE YOUR JUDGMENT):**

Ask yourself: **"Are these patterns sufficient for THIS specific use case?"**

✅ **Patterns are sufficient IF:**
- Patterns directly address this use case
- Patterns are recent/current (not outdated)
- Patterns cover the specific integration/features needed
- You're confident in the approach

❌ **Supplement with Context7 IF:**
- Patterns are outdated or incomplete
- This use case has unique requirements not covered
- Library has had major version changes since patterns created
- You need verification or more specific details
- **You have ANY doubt about pattern applicability**

**Important:** Pattern library provides a **baseline**, not a constraint. You are **encouraged** to call Context7 when it would improve specification quality, even if patterns exist.

#### Step 2: Context7 Research (Supplement or Fallback)

**Call Context7 when:**
- No patterns found in pattern library, OR
- Patterns exist but are insufficient/outdated for this use case, OR
- You need fresh documentation to verify or supplement patterns

```python
# For libraries without pattern matches, use Context7
for library in libraries_needing_context7:
    print(f"\n📚 Researching {library} via Context7...")

    # Step 1: Resolve library ID
    print(f"   Step 1/2: Resolving library ID...")
    lib_result = mcp__context7__resolve-library-id(libraryName=library)

    if not lib_result or len(lib_result) == 0:
        print(f"   ❌ Library not found in Context7")
        print(f"   → Manual research required for {library}")
        continue

    lib_id = lib_result[0]['id']  # Use first match
    print(f"   ✅ Resolved to: {lib_id}")

    # Step 2: Get documentation (focused on use case)
    print(f"   Step 2/2: Fetching documentation...")

    # Extract topic from user answers (or use generic)
    topic = "integration and best practices"  # Customize per library

    docs = mcp__context7__get-library-docs(
        context7CompatibleLibraryID=lib_id,
        topic=topic,
        tokens=5000
    )

    # Save documentation
    docs_file = f"${EPIC_DIR}/research/{library.lower()}-context7.md"
    with open(docs_file, 'w') as f:
        f.write(f"# {library} Documentation (Context7)\n\n")
        f.write(f"**Library ID:** {lib_id}\n")
        f.write(f"**Topic:** {topic}\n")
        f.write(f"**Retrieved:** $(date +%Y-%m-%d)\n\n")
        f.write("---\n\n")
        f.write(docs)

    print(f"   📄 Saved to: research/{library.lower()}-context7.md")
    print(f"   ✅ ACCEPT - Documentation retrieved")
    print(f"   🔄 Auto-queued for pattern extraction")
```

**What happens with Context7 results:**
- Documentation saved to `.tasks/backlog/EPIC-XXX/research/<library>-context7.md`
- **Automatically queued for extraction** (via PostToolUse hook)
- Extract patterns later with `/extract-patterns`
- Extracted patterns improve pattern library for future specs

#### Step 3: Document Research Results (MANDATORY)

Create a summary of all research performed:

```bash
echo ""
echo "📝 Creating research summary..."
echo ""

cat > "${EPIC_DIR}/research/README.md" << 'README_EOF'
# Research Summary for ${EPIC_ID}

**Epic:** ${TITLE}
**Created:** $(date +%Y-%m-%d)

## External Dependencies Researched

$(for lib in ${DETECTED_LIBRARIES//,/ }; do
    lib=$(echo $lib | xargs)  # Trim whitespace

    # Check which research method was used
    if [ -f "${EPIC_DIR}/research/${lib,,}-patterns.md" ]; then
        echo "### $lib"
        echo "- **Source:** Pattern Library"
        echo "- **Patterns Used:** $(grep -c '^## Pattern:' ${EPIC_DIR}/research/${lib,,}-patterns.md 2>/dev/null || echo 0) pattern(s)"
        echo "- **File:** \`${lib,,}-patterns.md\`"
        echo ""
    elif [ -f "${EPIC_DIR}/research/${lib,,}-context7.md" ]; then
        echo "### $lib"
        echo "- **Source:** Context7 (fresh documentation)"
        echo "- **Status:** Auto-queued for pattern extraction"
        echo "- **File:** \`${lib,,}-context7.md\`"
        echo ""
    else
        echo "### $lib"
        echo "- **Source:** Not researched (manual research required)"
        echo "- **Status:** ⚠️ Pending"
        echo ""
    fi
done)

## No External Dependencies

_Check this section if this epic uses only built-in functionality._

- [ ] Confirmed: No external libraries required
- [ ] Justification: ___________

## Next Steps

- [ ] Review all research documents before architecture design
- [ ] Apply patterns from pattern library to specification
- [ ] Extract Context7 docs to pattern library (run `/extract-patterns`)
- [ ] Update this summary if additional dependencies discovered

README_EOF

echo "✅ Research summary created: ${EPIC_DIR}/research/README.md"
echo ""
```

---

### Skip Conditions (RARE)

**Only skip library research if ALL conditions met:**

1. ✅ No external libraries detected in dependency analysis
2. ✅ User explicitly confirms no external dependencies
3. ✅ Specification uses only built-in/standard library functionality

**If ANY external library is used, research is MANDATORY.**

---

### Why This Workflow Matters

#### Pattern Library First (Baseline - Saves 5-15k tokens when sufficient)

- **Curated patterns:** Proven implementations from past projects
- **Consistency:** Ensures similar problems solved similarly
- **Fast:** Local semantic search via Ollama (<20ms)
- **Usage-boosted:** Popular patterns ranked higher

#### Context7 Supplement (Quality - Use when patterns need verification/updating)

- **Up-to-date:** Latest library documentation and best practices
- **Comprehensive:** 5k tokens focused on specific use case
- **Self-improving:** Auto-queued for extraction → grows pattern library
- **Quality assurance:** Never be blocked by outdated/insufficient patterns

**USE YOUR JUDGMENT:** Call Context7 even if patterns exist, when you need verification or more current/specific information.

#### Continuous Improvement Loop

```
User Query
    ↓
Pattern Library Search (ALWAYS)
    ↓
    ├─ Patterns sufficient → Use patterns ✅
    │
    ├─ Patterns exist but need verification → Patterns + Context7 ✅✅
    │
    └─ No patterns → Context7 only
                      ↓
                  Save docs + Auto-queue
                      ↓
                  /extract-patterns
                      ↓
                  New patterns added to library
                      ↓
                  Future queries: patterns + optional Context7 ✨
```

**Philosophy:** Pattern library for efficiency, Context7 for quality. Use both when needed.

---

### Validation

**Before proceeding to architecture design, verify:**

```bash
echo ""
echo "🔍 Validating research completeness..."
echo ""

research_complete=true

# Check if README exists
if [ ! -f "${EPIC_DIR}/research/README.md" ]; then
    echo "❌ Research summary missing: research/README.md"
    research_complete=false
fi

# Check that each detected library was researched
for lib in ${DETECTED_LIBRARIES//,/ }; do
    lib=$(echo $lib | xargs | tr '[:upper:]' '[:lower:]')

    if [ ! -f "${EPIC_DIR}/research/${lib}-patterns.md" ] && \
       [ ! -f "${EPIC_DIR}/research/${lib}-context7.md" ]; then
        echo "⚠️  Library not researched: $lib"
        research_complete=false
    fi
done

if [ "$research_complete" = true ]; then
    echo "✅ All external dependencies researched"
    echo ""
    echo "Proceeding to architecture design..."
else
    echo ""
    echo "❌ Research incomplete - cannot proceed to architecture"
    echo "   Complete research for all libraries before continuing"
    exit 1
fi

echo ""
```

**Research gate:** Architecture design cannot proceed until all dependencies researched.

---
