---
description: "Interactive refinement of existing epic specifications with clarity checks and validation"
argument-hint: "EPIC-ID"
---

## Objective

Refine an existing epic specification through interactive conversation using clarity-first methodology.

**This is a conversation-driven review**, not a script. I'll read your epic and ask clarifying questions to improve it.

## Process: Guided Refinement

## Phase 1: Read Current Specification

**I'll examine:**
- `spec.md` - High-level WHAT/WHY
- `architecture.md` - System design HOW
- `task.md` - Workflow integration and frontmatter

**Current epic context:**
- Epic: $ARGUMENTS
- Project status: Check for uncommitted changes or GitHub sync issues

## Phase 2: Clarity Assessment

**I'll evaluate clarity on 4 dimensions:**

### 1. Problem Clarity
**Questions I'll ask:**
- Is the problem statement specific enough?
- Can I identify the user and their pain point?
- Is the business impact quantified?

**Example issue:**
> ❌ "Improve email search"
> ✅ "Users waste 30 min/day finding emails because keyword search misses semantically similar results (e.g., 'meeting notes' doesn't find 'discussion summary')"

### 2. User Scenario Clarity
**Questions I'll ask:**
- Are scenarios concrete and specific?
- Do they describe observable behavior?
- Is success measurable?

**Example improvement:**
> ❌ "User searches for emails better"
> ✅ "User types 'project deadline', system returns emails about 'submission date' and 'due date' ranked by relevance, user finds target email in <10 seconds"

### 3. Requirement Testability
**Questions I'll ask:**
- Can each requirement be validated?
- Are acceptance criteria measurable?
- Are constraints explicit? (performance, scale, compatibility)

**Example refinement:**
> ❌ "System should be fast"
> ✅ "Search returns results in <200ms for 10k email corpus (p95)"

### 4. Implementation Feasibility
**Questions I'll ask:**
- Are dependencies clear and available?
- Are integration points documented?
- Is the scope realistic for the timeline?
- Are edge cases and error handling addressed?

**Example clarification:**
> ❌ "Integrate with AI service"
> ✅ "Use OpenAI embeddings API (requires API key in env), fall back to local sentence-transformers if unavailable, handle rate limiting with exponential backoff"

## Phase 3: Interactive Refinement

**For each clarity issue, I'll:**
1. Point out the ambiguity
2. Ask clarifying questions
3. Suggest improved wording
4. Validate your response

**Example conversation:**

**Me:**
> I see your spec says "AI-powered email classification."
>
> **Clarity questions:**
> - What categories? (personal, work, spam, urgent, etc.)
> - How accurate? (90%, 95%, 99%)
> - What happens on misclassification? (user can correct, auto-relearn)
> - Performance requirement? (<100ms, <1sec)

**You:**
> "Work/personal/spam, 95% accuracy, user can reclassify with one click"

**Me:**
> Great! I'll update the functional requirement to:
>
> ```markdown
> ### FR-2: Email Classification
> **Description:** System MUST classify emails into work/personal/spam
> **Acceptance Criteria:**
> - Classification accuracy >95% on test dataset
> - Inference latency <100ms per email (p95)
> - User can reclassify with single click
> - System learns from user corrections (accuracy improves over time)
> ```

## Phase 4: Missing Elements Check

**I'll identify gaps:**

### Common Missing Elements
- **Performance Requirements:** Latency, throughput, scale
- **Error Handling:** What happens when operations fail?
- **Data Privacy:** Where is data stored? Who can access it?
- **Integration Points:** What existing systems does this touch?
- **Migration Path:** How do existing users transition?
- **Testing Strategy:** How will we verify correctness?
- **Edge Cases:** What unusual scenarios need handling?

**For each gap, I'll ask:**
- "Have you thought about X?"
- "What should happen when Y?"
- "Do we need to document Z?"

## Phase 5: Architecture Alignment

**I'll check spec.md vs architecture.md consistency:**

**Questions:**
- Does architecture.md support all requirements in spec.md?
- Are components in architecture.md mentioned in spec.md?
- Do data model and API design match functional requirements?
- Are performance requirements reflected in architecture decisions?

**Example misalignment:**
> **spec.md:** "Search 10k emails in <200ms"
> **architecture.md:** "PostgreSQL full-text search"
>
> **Me:** "Full-text search on 10k rows might not hit <200ms consistently. Should we consider vector search with pgvector or an inverted index? Want me to research options via Context7?"

## Phase 6: GitHub Sync Check

**I'll verify task management hygiene:**

**Checks:**
- Are there uncommitted changes in the epic directory?
- Is the task synced to GitHub Issues?
- Are all artifacts properly tracked in git?

**Commands I'll run:**
```bash
# Check for uncommitted changes
git status .tasks/backlog/$EPIC_ID/
git status .tasks/current/$EPIC_ID/

# Verify GitHub Issue sync (if applicable)
# Suggest creating issue if missing
```

## Phase 7: Research Recommendations

**Based on requirements, I'll suggest research:**

### Pattern Library Search (First)
**I'll search local pattern library before external research:**
```
/pattern search "vector search implementation"
/pattern search "async email processing"
```

**Benefit:** Reuse established patterns from this or similar projects

### Context7 Research (If Needed)
**I'll suggest Context7 for new dependencies:**

**Example:**
> "Your vector search requirement needs library research:
> - txtai (lightweight, Python-native)
> - pgvector (PostgreSQL extension)
> - Pinecone (managed service)
>
> Want me to research these now with Context7?"

**Workflow:**
1. Search pattern library first (60-70% hit rate)
2. Use Context7 for new/unfamiliar libraries
3. Capture Context7 results for future pattern library

## Phase 8: Apply Refinements

**Once we've converged on improvements:**

1. I'll update `spec.md` with clearer problem statement, scenarios, requirements
2. I'll update `architecture.md` with aligned components, data model
3. I'll update `task.md` frontmatter with metadata
4. I'll commit changes to git with descriptive message

**You approve changes, I apply them.**

---

## Example Interaction

**You:** `/refine-spec EPIC-007`

**Me:**
```
Reading EPIC-007: Real-Time Email Search...

## Clarity Assessment

### ✅ Strong Areas
- Problem statement is specific: "Users waste time with keyword-only search"
- User scenarios are concrete with timing (<10 seconds)
- Performance requirements are quantified (<200ms)

### ⚠️ Needs Clarification

**1. Semantic Similarity Algorithm**
Your spec mentions "semantic similarity" but doesn't specify:
- What embedding model? (sentence-transformers, OpenAI, txtai)
- What similarity threshold? (cosine >0.7, >0.8, >0.9)
- How to handle multiple similar results? (ranking, grouping)

**2. Index Update Strategy**
When new emails arrive:
- Immediate embedding + indexing? (latency impact)
- Batch processing? (staleness concern)
- Incremental updates? (complexity)

**3. Fallback Behavior**
If vector search fails:
- Fall back to keyword search?
- Show error to user?
- Queue for retry?

Let's address these. Tell me your thoughts on #1 (embedding model).
```

**You respond, I ask follow-ups, we refine together, I apply changes.**

---

## Validation Before Completion

**Before marking refinement complete, I'll verify:**

1. **All 4 clarity dimensions addressed** (Problem, Scenario, Testability, Feasibility)
2. **Missing elements documented** (performance, error handling, etc.)
3. **Architecture aligned with spec** (no contradictions)
4. **Research recommendations captured** (pattern library or Context7)
5. **Git status clean** (all changes committed)
6. **GitHub sync verified** (issue created/updated if applicable)

---

## Your Turn

**Tell me the EPIC-ID you want to refine, and I'll:**
1. Read the current specification
2. Identify clarity issues
3. Ask clarifying questions
4. Guide you through improvements
5. Update the specification

**Which epic should we refine?**

---

## Timing

This command runs **between spec creation and execution:**

```
/spec-epic EPIC-007
    ↓
/refine-spec EPIC-007  ← Interactive clarity refinement
    ↓
/execute-workflow EPIC-007  ← Ready for implementation
```

---

## Output

All refinements saved atomically to `.tasks/backlog/{EPIC-ID}/` or `.tasks/current/{EPIC-ID}/`.

**Git tracking recommended:**
```bash
git add .tasks/backlog/EPIC-007/
git commit -m "refine(EPIC-007): Clarified semantic search requirements"
```

---

## Integration with Tier 1 Workflow

This command focuses on **clarity-first methodology** without artifact generation complexity:
- No contract regeneration (Tier 1 doesn't have contract tooling)
- No constitutional validation (Tier 1 doesn't have constitution.md)
- No graph-server analysis (Tier 1 doesn't have code graph)
- Pattern library search for reusable knowledge
- Context7 research for new dependencies
- GitHub sync checks for task hygiene

**All refinement is conversational and interactive** - I ask questions, you clarify, we improve the spec together.
