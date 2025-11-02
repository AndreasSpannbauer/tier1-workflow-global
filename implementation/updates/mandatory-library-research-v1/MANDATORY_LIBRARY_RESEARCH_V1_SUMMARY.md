# Mandatory Library Research V1 - Update Summary

**Update ID:** `mandatory-library-research-v1`
**Date:** 2025-10-25
**Priority:** Critical
**Status:** ✅ Complete - Content Created, Test Applied

---

## Purpose

Enforce **Pattern Library → Context7** research workflow during spec creation to ensure:
1. Pattern library is actively queried (currently underutilized)
2. Context7 is called with proper judgment (not avoided, not overused)
3. Pattern library grows through Context7 extraction queue

---

## Key Philosophy (Revised per User Feedback)

### ❌ NOT the Goal
- "Pattern library OR Context7" (exclusive choice)
- Prevent Context7 calls
- Make pattern library a gatekeeper

### ✅ ACTUAL Goal
- "Pattern library AND optionally Context7" (additive)
- **Efficiency:** Start with patterns (baseline, saves tokens)
- **Quality:** Supplement with Context7 when needed (verification, updates, specialization)
- **Judgment:** Claude decides when Context7 adds value, even if patterns exist

---

## Workflow

### Step 1: Pattern Library Search (ALWAYS - Baseline)

**For every external library:**
```python
mcp__pattern-library__search_patterns(
    query="<library-name> <use-case>",
    mode="auto",
    top_k=5
)
```

**Retrieve patterns → Review → Save to research/**

### Step 2: Context7 Research (Supplement or Fallback)

**Call Context7 when (USE YOUR JUDGMENT):**

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

```python
# Context7 supplement
lib_id = mcp__context7__resolve-library-id(libraryName="<library>")
docs = mcp__context7__get-library-docs(
    context7CompatibleLibraryID=lib_id,
    topic="<specific-topic>",
    tokens=5000
)
```

**Auto-queued for extraction** → `/extract-patterns` → Pattern library grows

---

## Files Created

### 1. Update Definition
**File:** `implementation/update_definitions.json`

```json
{
  "id": "mandatory-library-research-v1",
  "version": "1.0.0",
  "date": "2025-10-25",
  "description": "Enforce Pattern Library → Context7 research workflow...",
  "priority": "critical",
  "components": [...]
}
```

### 2. Content Fragments

#### spec-epic.md Section (373 lines)
**File:** `implementation/updates/mandatory-library-research-spec-epic-section.md`

**Inserts before:** `## Generate Epic ID`

**Contains:**
- Library dependency detection (Python script)
- Pattern library search workflow
- Context7 supplement workflow
- Research documentation (research/README.md)
- Validation checks

#### spec-architect-template.md Section (310+ lines)
**File:** `implementation/updates/mandatory-library-research-spec-architect-section.md`

**Replaces:** `## Mandatory Pre-Specification Analysis` through `### 3. Graph-Server Intelligence`

**Contains:**
- Identify external dependencies
- Pattern library search (baseline)
- Context7 research (supplement/fallback)
- Research documentation
- Skip conditions (rare)
- Philosophy and continuous improvement loop

---

## Test Application

**Project:** whisper_hotkeys

**Files Updated:**
- `.claude/commands/spec-epic.md` (inserted 373-line research section)
- `.claude/output-styles/spec-architect-template.md` (replaced pre-spec analysis section)

**Validation:**
```bash
✅ "Research External Libraries (MANDATORY)" present
✅ "USE YOUR JUDGMENT" guidance present
✅ "Supplement with Context7 IF (even if patterns exist)" present
✅ Philosophy section emphasizes efficiency + quality
```

---

## Deployment to Other Projects

### Manual Application (Current Method)

For each project with Tier1 workflow:

```bash
PROJECT_PATH="<project-path>"

# Update spec-epic.md
cd $PROJECT_PATH/.claude/commands
cp spec-epic.md spec-epic.md.backup
sed -i '/^## Generate Epic ID$/e cat /home/andreas-spannbauer/tier1_workflow_global/implementation/updates/mandatory-library-research-spec-epic-section.md' spec-epic.md

# Update spec-architect-template.md
cd $PROJECT_PATH/.claude/output-styles
cp spec-architect-template.md spec-architect-template.md.backup
sed -i '175,232d' spec-architect-template.md
sed -i '174r /home/andreas-spannbauer/tier1_workflow_global/implementation/updates/mandatory-library-research-spec-architect-section.md' spec-architect-template.md

echo "✅ Updated $PROJECT_PATH"
```

### Automated Deployment (TODO)

**Option 1:** Build surgical update system
- Create `tools/apply_update.py` script
- Create `/tier1-update-surgical` command
- Use `update_definitions.json` metadata

**Option 2:** Simple bash script
- Loop through projects from registry
- Apply sed commands to each
- Track applied updates

---

## Expected Outcomes

### Immediate
1. ✅ Pattern library queried in every spec creation
2. ✅ Context7 called with proper judgment (not avoided, not abused)
3. ✅ Research phase becomes mandatory (architecture cannot proceed without it)

### Medium Term
1. Pattern library grows through Context7 extraction
2. Specifications become more consistent (reusing proven patterns)
3. Token usage optimized (patterns save 5-15k tokens when sufficient)

### Long Term
1. Pattern library covers most common use cases
2. Context7 primarily used for verification and specialization
3. Continuous improvement loop: Context7 → extraction → patterns → auto-injection

---

## Key Improvements from User Feedback

**Original Design:**
- Pattern library as "fallback only" gatekeeper
- Context7 only when patterns missing
- Binary choice: patterns OR Context7

**Revised Design (Current):**
- Pattern library as **baseline** (starting point)
- Context7 **supplement** when needed (verification, updates, specialization)
- Additive approach: patterns AND Context7 when judgment says it's valuable
- Explicit encouragement: "You are encouraged to call Context7 when it would improve quality, even if patterns exist"

**Philosophy shift:**
- FROM: "Avoid Context7 to save tokens"
- TO: "Start with patterns for efficiency, supplement with Context7 for quality"

---

## Next Steps

1. **Decision:** Choose deployment method
   - Manual application to all projects (5-10 projects)
   - Build surgical update system (reusable for future updates)
   - Simple bash loop script

2. **Apply to all projects** in registry

3. **Test in real spec creation** - create a spec that uses external libraries

4. **Monitor pattern library growth**
   - Run `/extract-patterns` on queued Context7 calls
   - Verify patterns are being created and indexed

5. **Iterate based on usage**
   - Are specs consistently calling pattern library?
   - Is Context7 being called with good judgment?
   - Is pattern library growing?

---

## Files Reference

**Update definition:**
- `implementation/update_definitions.json` (updated)

**Content fragments:**
- `implementation/updates/mandatory-library-research-spec-epic-section.md` (373 lines)
- `implementation/updates/mandatory-library-research-spec-architect-section.md` (310+ lines)

**Test project:**
- `~/whisper_hotkeys/.claude/commands/spec-epic.md` (updated)
- `~/whisper_hotkeys/.claude/output-styles/spec-architect-template.md` (updated)

**Backups:**
- `~/whisper_hotkeys/.claude/commands/spec-epic.md.backup`
- `~/whisper_hotkeys/.claude/output-styles/spec-architect-template.md.backup`

---

**Status:** ✅ Ready for deployment to all projects
**Next Action:** Choose deployment method and apply to remaining projects
