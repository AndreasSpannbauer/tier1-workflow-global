---
description: "Get ChatGPT implementation help with automated file upload"
allowed-tools: [Bash, Read, Write, mcp__playwright__browser_snapshot, mcp__playwright__browser_type, mcp__playwright__browser_click, mcp__playwright__browser_wait_for]
argument-hint: "EPIC-ID [--scope=backend|frontend|fullstack-review]"
---

Get ChatGPT's help implementing an EPIC. Upload helper handles boring setup (navigate, authenticate, upload files), then YOU take over for intelligent interaction (prompting, response parsing, patch extraction).

## Architecture: Separation of Concerns

**Upload Helper (Python script):**
- ✅ Open browser and navigate to ChatGPT
- ✅ Authenticate if needed (gopass credentials)
- ✅ Upload repomap + MASTER_SPEC.md
- ✅ Return control to Claude

**Claude (YOU - intelligent interaction):**
- ✅ Generate contextual prompt based on EPIC
- ✅ Send prompt via MCP browser tools
- ✅ Monitor response completion
- ✅ Extract patches from response
- ✅ Apply patches with git apply

## Context
- Current working directory: !`pwd`
- Available EPICs: !`ls -1 .tasks/backlog/ | grep EPIC`
- Upload helper: `tools/chatgpt_upload_helper.py`

## Your Task

### Phase 1: Parse Arguments and Analyze EPIC

1. **Extract arguments:**
   - EPIC-ID from $ARGUMENTS (e.g., "EPIC-025")
   - Optional --scope flag (default: auto-detect from domain)

2. **Read EPIC spec:**
   - Location: `.tasks/backlog/EPIC-{ID}-{Name}/spec.md`
   - Extract: domain, objective, requirements, acceptance criteria

3. **Determine scope:**
   - Database domain → `backend`
   - Backend domain → `complete-backend`
   - Frontend domain → `frontend`
   - Full-stack → `fullstack-review`
   - Or use explicit --scope if provided

### Phase 2: Upload Files (Automated)

Run the upload helper script:

```bash
python3 tools/chatgpt_upload_helper.py --scope {detected-scope}
```

**What this does:**
- Generates repomap for the scope
- Opens ChatGPT in browser (via MCP)
- Authenticates if needed (may pause for 2FA)
- Uploads repomap + MASTER_SPEC.md
- Returns control to you

**Wait for:** "✅ Setup complete! Claude will now take over..."

### Phase 3: Generate Contextual Prompt

Analyze the EPIC and create an intelligent, focused prompt:

**Template:**
```
EPIC-{ID}: {Title}

Objective: {epic objective}

Context:
- Project: {project type, stack, patterns}
- Domain: {backend/frontend/fullstack}
- Key files: {relevant existing files}

Requirements:
{numbered list of requirements from EPIC}

Focus Areas:
{specific architectural concerns, patterns to follow, edge cases}

Output Format:
Provide implementation as git-compatible unified diff patches:
- One patch per logical component
- Include file paths in standard diff format
- Add comprehensive tests
- Follow existing code patterns

Example patch naming:
- EPIC-{ID}-01-database-schema.patch
- EPIC-{ID}-02-service-implementation.patch
- EPIC-{ID}-03-tests.patch
```

### Phase 4: Send Prompt (You handle via MCP)

1. **Take browser snapshot:**
   ```
   Use mcp__playwright__browser_snapshot to see current page state
   ```

2. **Find message input:**
   - Look for textarea/input element
   - Extract element ref from snapshot

3. **Type prompt:**
   ```
   Use mcp__playwright__browser_type with:
   - element: "message textarea"
   - ref: {extracted ref}
   - text: {your generated prompt}
   - submit: true (or click send button)
   ```

### Phase 5: Monitor Response (You handle via MCP)

1. **Wait for completion:**
   - Use `mcp__playwright__browser_wait_for` or periodic snapshots
   - Look for: "Regenerate" button, "Copy code" buttons, no "Stop generating"

2. **Check every 15-30 seconds:**
   - Take snapshot: `mcp__playwright__browser_snapshot`
   - Check if still generating (look for "thinking", "generating")
   - Continue until complete

3. **Max timeout: 10 minutes**

### Phase 6: Extract Response (You handle intelligently)

1. **Take final snapshot:**
   ```
   Use mcp__playwright__browser_snapshot to get complete response
   ```

2. **Parse response text:**
   - Extract text content from accessibility snapshot
   - Identify code blocks (look for ```diff, ```python, etc.)
   - Extract patch content

3. **Save patches as files:**
   - Parse unified diff format
   - Save to: `EPIC-{ID}-01-{description}.patch`
   - Preserve exact formatting

### Phase 7: Apply Patches

1. **Dry-run each patch:**
   ```bash
   git apply --check EPIC-{ID}-01-*.patch
   ```

2. **Apply if valid:**
   ```bash
   git apply EPIC-{ID}-01-*.patch
   ```

3. **Verify:**
   ```bash
   git status
   git diff
   ```

### Phase 8: Validate and Report

1. **Run validation:**
   - Project tests if available
   - Syntax checks
   - Build if applicable

2. **Display summary:**
   ```
   ✅ EPIC-{ID} Implementation Complete

   Patches Applied:
   - EPIC-{ID}-01-database-schema.patch
   - EPIC-{ID}-02-service-implementation.patch
   - EPIC-{ID}-03-tests.patch

   Files Changed:
   M  src/models/user.py
   M  src/services/email.py
   A  tests/test_email_service.py

   Next Steps:
   1. Review changes: git diff
   2. Run tests: npm run test / pytest
   3. Validate: npm run validate-all
   4. Commit: git add . && git commit -m "feat: Implement EPIC-{ID}"
   ```

## Example Usage

```bash
# Auto-detect scope from EPIC domain
/chatgpt-implement EPIC-025

# Override scope
/chatgpt-implement EPIC-025 --scope=fullstack-review
```

## Error Handling

### EPIC Not Found
```
❌ EPIC-{ID} not found

Available EPICs:
  ls -1 .tasks/backlog/ | grep EPIC
```

### Upload Helper Failed
```
❌ Upload failed

Troubleshooting:
1. Check MCP server: ps aux | grep playwright
2. Restart MCP: ~/bin/start-playwright-extension.sh
3. Verify gopass: gopass show chatgpt_user
```

### Gopass Not Configured
```
❌ Credentials not found

Setup:
1. gopass insert chatgpt_user  # Your ChatGPT email
2. gopass insert chatgpt_pw    # Your password
```

### Response Parsing Issues

If patches aren't in standard unified diff format:
1. Manually review response in browser
2. Copy patches to files manually
3. Ask ChatGPT to regenerate in proper format

### Patch Application Failed

```bash
# Check what's wrong
git apply --check EPIC-{ID}-01-*.patch

# Try with reject files (for conflicts)
git apply --reject EPIC-{ID}-01-*.patch

# Review reject files
cat *.rej
```

## Tips for Best Results

1. **Be specific in prompts:**
   - Reference exact file paths from repomap
   - Mention existing patterns to follow
   - Request test coverage explicitly

2. **Verify scope coverage:**
   - Check repomap includes relevant files
   - Use larger scope if files are missing

3. **Ask for proper format:**
   - Explicitly request unified diff patches
   - Specify git apply compatibility
   - Request separate patches per component

4. **Iterate if needed:**
   - If response isn't perfect, ask for refinements
   - Use "Regenerate" in ChatGPT
   - Provide more context if needed

## Notes

- **No state persistence:** Each run is fresh (no .chatgpt_session_state.json)
- **Claude handles complexity:** You parse responses intelligently, not brittle regex
- **Flexible:** You adapt to ChatGPT UI changes in real-time
- **Interactive:** You can have multi-turn conversations with ChatGPT as needed
