## Round 1: Problem Understanding - FIXED VERSION

**CRITICAL:** Do NOT just dump questions. Provide intelligent analysis first.

### Step 1: Analyze the Epic Title

Before asking questions, analyze what the user wants to build based on the epic title (`$ARGUMENTS`).

**Output:**
```markdown
## Round 1: Problem Understanding

I see you want to create: **"$ARGUMENTS"**

Let me analyze what this suggests:
- [Describe what kind of problem this epic seems to address based on the title]
- [Identify the probable user pain point]
- [Suggest likely technical approach]
- [Note any ambiguities that need clarification]

Now I'll ask 4 questions to refine the specification. For each question, I'll provide:
- Context (why this matters)
- Suggested options (based on my analysis)
- My recommendation (what I think makes sense)

Feel free to use my suggestions or provide your own answers.

---
```

### Step 2: Ask Question 1 - WITH CONTEXT

```markdown
### Question 1: Pain Point

**What user pain point does this solve?**

**Why this matters:** This defines the "why" - without a clear pain point, we risk building something nobody needs.

**Based on the epic title "$ARGUMENTS", I think the pain point might be:**
- Option A: [Specific pain point #1 related to the title]
- Option B: [Specific pain point #2 related to the title]
- Option C: [Specific pain point #3 related to the title]

**My recommendation:** [Your assessment of which option fits best, or a synthesis]

**Your answer:**
[Leave space for user to respond]
```

### Step 3: Ask Question 2 - WITH CONTEXT

```markdown
### Question 2: Current Workaround

**What is the current manual workaround?**

**Why this matters:** Understanding the current approach helps us design a solution that actually improves the workflow (not just changes it).

**Likely current workarounds for "$ARGUMENTS":**
- Manual process: [Describe likely manual steps]
- Existing tool: [Mention tools that might currently be used]
- Partial automation: [Describe semi-automated approaches]

**My recommendation:** [Which workaround to focus on replacing, or if multiple exist]

**Your answer:**
[Leave space for user to respond]
```

### Step 4: Ask Question 3 - WITH CONTEXT

```markdown
### Question 3: Desired Automated Behavior

**What is the desired automated behavior?**

**Why this matters:** This defines success - what does "working perfectly" look like?

**For "$ARGUMENTS", the ideal automation might:**
- Scenario 1: [Describe first automation scenario]
- Scenario 2: [Describe second automation scenario]
- Scenario 3: [Describe third automation scenario]

**My recommendation:** [Which scenario provides best ROI, or a hybrid approach]

**Your answer:**
[Leave space for user to respond]
```

### Step 5: Ask Question 4 - WITH CONTEXT

```markdown
### Question 4: Expected Impact

**What is the expected impact? (users affected, time saved, business value)**

**Why this matters:** Justifies the investment - helps prioritize against other epics.

**Estimated impact for "$ARGUMENTS":**
- Users affected: [Estimate based on epic scope]
- Time savings: [Estimate hours/week saved]
- Business value: [Describe value proposition]
- Frequency: [How often will this be used]

**My recommendation:** [Your assessment of ROI]

**Your answer:**
[Leave space for user to respond]
```

### Step 6: Wait for All Answers

**Instruction:** Wait for user to provide all 4 answers before proceeding to Round 2.

---

## Example Output (How It Should Look)

```markdown
## Round 1: Problem Understanding

I see you want to create: **"Component Audit & Migration Planning - SCALAR Architecture Discovery"**

Let me analyze what this suggests:
- This appears to be about **discovering and documenting the existing architecture** of the SCALAR project
- The pain point is likely **lack of visibility** into how components are structured and interconnected
- The technical approach probably involves **static code analysis** and **dependency mapping**
- Key ambiguity: Are we migrating TO something or just auditing the current state?

Now I'll ask 4 questions to refine the specification. For each question, I'll provide:
- Context (why this matters)
- Suggested options (based on my analysis)
- My recommendation (what I think makes sense)

---

### Question 1: Pain Point

**What user pain point does this solve?**

**Why this matters:** This defines the "why" - without a clear pain point, we risk building something nobody needs.

**Based on the epic title, I think the pain point might be:**
- Option A: **Can't understand codebase structure** - New developers (or you after time away) struggle to understand how SCALAR components fit together
- Option B: **Risk of breaking changes** - Making changes is risky because dependencies between components aren't documented
- Option C: **Planning paralysis** - Can't plan migrations or refactors because current state is unclear

**My recommendation:** Probably a combination of A and B - you need visibility for safe changes.

**Your answer:**
```

This makes it MUCH more useful!
