---
description: "Interactive master specification creation for project vision and principles"
---

## Objective

Create or refine the project's Master Specification - the highest-level document that defines product vision, core principles, and strategic direction.

## What is the Master Specification?

The Master Spec sits above all implementation details. It defines:
- **Product Vision:** What are we building and why?
- **Core Principles:** What matters most? (speed, simplicity, reliability)
- **Success Metrics:** How do we measure product success?
- **Target Users:** Who are we building for?
- **Non-Goals:** What are we explicitly NOT doing?

**Location:** `.tasks/MASTER_SPEC.md`

## Process: Interactive Refinement

This is a **guided conversation**, not a script. I'll ask you clarifying questions to create a clear, actionable master specification.

### Phase 1: Product Vision (WHY THIS EXISTS)

**I'll ask you:**

**1. The Big Problem:**
- What fundamental problem does this project solve?
- Why is the current state unacceptable?
- What inspired this project?

**Example response:**
> "Task management is fragmented across tools and context gets lost.
> Existing tools don't capture the 'why' behind decisions.
> We're building a simple, git-integrated task system that preserves context."

**2. Vision Statement:**
- If wildly successful, what does the world look like in 3 years?
- What becomes effortless that is currently painful?
- What do users say about this product?

**3. Strategic Bets:**
- What technology or approach makes this possible now? (AI, git integration, etc.)
- What assumptions are we making?
- What could invalidate this vision?

### Phase 2: Core Principles (HOW WE BUILD)

**I'll help you define 3-5 core principles:**

**Examples:**
- **Simplicity First:** Max 3 major components, no speculative features
- **Git-Native:** All state tracked in version control
- **Local-First:** Works offline, no cloud dependency
- **Fast by Default:** <100ms response time for all operations

**For each principle:**
- **Name:** Short, memorable
- **Statement:** Clear declaration
- **Rationale:** Why this matters
- **Enforcement:** How we maintain this

### Phase 3: Target Users & Use Cases

**I'll help you define primary personas:**

**For each persona:**
- **Name & Role:** "Alex, Solo Developer"
- **Core Problem:** Loses context between sessions, forgets decisions
- **Key Use Cases:** Track tasks, preserve decisions, search history
- **Success Metric:** Reduces "what was I working on?" time by 80%

**We'll identify:**
- Primary users (80% of value)
- Secondary users (20% of value)
- Explicitly excluded users (we're NOT building for...)

### Phase 4: Success Metrics (WHAT GOOD LOOKS LIKE)

**Product-level metrics:**
- User satisfaction (retention, daily use)
- Performance (latency, resource usage)
- Business impact (time saved, productivity gain)

**Example:**
```markdown
## Success Metrics

### User Satisfaction
- **Daily active usage** within 1 week of install
- **90% retention** after 30 days
- **<5% abandonment** rate

### Performance
- **<100ms** response time (p95)
- **<10MB** disk space for typical project
- **<50ms** startup time

### Business Impact
- **80% reduction** in "what was I doing?" context switching time
- **100% context preservation** across sessions
- **Zero external dependencies** for core functionality
```

### Phase 5: Non-Goals & Boundaries (WHAT WE'RE NOT DOING)

**Critical for focus:**
- What adjacent problems are we NOT solving?
- What features will we deliberately exclude?
- What markets/users are out of scope?

**Example:**
```markdown
## Non-Goals

- **NOT a project management tool:** We don't manage teams or sprints
- **NOT a time tracker:** We won't track hours or billing
- **NOT a collaboration platform:** Single-user focus (for now)
- **NOT cloud-dependent:** Must work 100% offline
```

### Phase 6: Research Recommendations

Based on your vision, I'll suggest relevant research:

**Pattern Library First:**
- Search your existing pattern library: `mcp__unified_v6_server__search_pattern_library(query="...")`
- Check for existing patterns before external research

**Context7 Research (if needed):**
- "Your git integration needs research on: pygit2, GitPython, libgit2"
- "Your CLI design needs research on: click, typer, rich"
- "Your performance monitoring needs research on: pytest-benchmark, profiling"

I can run this research immediately if you want.

### Phase 7: GitHub Issue Creation

Once the master spec is complete, I'll help you:

**Create tracking issue:**
- Title: `[MASTER] Project Vision & Core Principles`
- Labels: `documentation`, `planning`
- Milestone: `v1.0`
- Body: Link to master spec + key principles summary

**Why:**
- Central reference point for all work
- Links all epics/features back to master vision
- Enables cross-referencing and traceability

### Phase 8: Write Master Specification

Once refined through conversation, I'll create `.tasks/MASTER_SPEC.md`:

**Structure:**
```markdown
# [Project Name] - Master Specification

## Vision Statement
[From Phase 1]

## Core Principles
[From Phase 2]

## Target Users
[From Phase 3]

## Success Metrics
[From Phase 4]

## Non-Goals
[From Phase 5]

## Technology Strategy
[From Phase 6]

## Implementation Roadmap (High-Level)
- Phase 1: [Core Infrastructure]
- Phase 2: [Key Features]
- Phase 3: [Polish & Optimization]
```

---

## Example Interaction

**You:** `/spec-master`

**Me:**
```
Let's create your project's master specification.

## Current State Analysis

Looking at your project structure, I can see:
- Task system with git integration
- Python-based implementation
- Pattern library for knowledge capture
- Focus on simplicity and local-first

## Vision Questions

1. **The Big Problem:**
   - Is the core problem "context loss" or something more specific?
   - Who suffers most from this? (solo devs, small teams, enterprises)
   - What makes existing solutions (Jira, Linear, GitHub Issues) insufficient?

2. **Your Vision:**
   - In 3 years, what do users say about this tool?
   - What becomes effortless that is currently painful?
   - Is this a personal tool, team tool, or open-source product?

3. **Strategic Bets:**
   - Why git-native vs. database? (simplicity, version control, auditability)
   - Why local-first vs. cloud? (privacy, speed, offline-first)
   - What assumptions could break this vision?

Tell me about your vision, and I'll ask follow-up questions to refine it.
```

**You respond, I guide you through Phases 1-8, asking clarifying questions, suggesting improvements, validating clarity.**

---

## Your Turn

**Do you want to:**
1. **Create a new Master Spec** - I'll guide you from scratch
2. **Refine existing vision** - I'll ask clarifying questions about current direction
3. **Research technologies** - I'll help identify libraries and patterns

**What's your starting point?**
