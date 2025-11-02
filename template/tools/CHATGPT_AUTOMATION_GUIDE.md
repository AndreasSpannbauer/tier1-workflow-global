# ChatGPT Upload Automation Guide

**Simple helper script + Claude's intelligence = Flexible, robust workflow**

## Overview

**Upload Helper (Python script)** handles boring repetitive tasks:
1. ✅ Open browser and navigate to ChatGPT
2. ✅ Authenticate if needed (gopass credentials + 2FA pause)
3. ✅ Upload repomap + MASTER_SPEC.md
4. ✅ Return control to Claude

**Claude (intelligent agent)** handles complex tasks:
1. ✅ Generate contextual prompts tailored to EPIC
2. ✅ Send prompts via MCP browser tools
3. ✅ Monitor response completion intelligently
4. ✅ Parse responses and extract patches
5. ✅ Apply patches with validation

**Benefits:**
- 🎯 **Simple:** Helper script is ~200 lines vs 839 lines
- 🔧 **Flexible:** Claude adapts to ChatGPT UI changes in real-time
- 🧠 **Intelligent:** Claude parses responses contextually, not brittle regex
- 🔄 **Interactive:** Claude can have multi-turn conversations as needed

---

## Architecture

### What the Helper Does (Boring Automation)

```python
# Open browser
await browser_navigate(url="https://chat.openai.com")

# Authenticate (may pause for 2FA)
if not logged_in:
    authenticate_with_gopass()
    input("Press Enter after 2FA...")

# Upload files
await browser_file_upload(paths=[
    "repomaps/repomap-fullstack-review.txt",
    ".tasks/MASTER_SPEC.md"
])

print("✅ Setup complete! Claude takes over now...")
```

### What Claude Does (Intelligence)

```
1. Analyze EPIC requirements
2. Generate contextual prompt
3. Send via: mcp__playwright__browser_type
4. Monitor via: mcp__playwright__browser_snapshot (periodic polling)
5. Extract patches from response text
6. Apply with: git apply
7. Validate and report
```

**Clean separation:** Script handles brittle browser automation, Claude handles intelligent interaction.

---

## Prerequisites

### Required

1. **Playwright MCP Extension** running:
   ```bash
   ~/bin/start-playwright-extension.sh
   ```

2. **Gopass credentials** (for automatic login):
   ```bash
   gopass insert chatgpt_user  # Your ChatGPT email
   gopass insert chatgpt_pw    # Your ChatGPT password
   ```

3. **MCP Python SDK**:
   ```bash
   pip install mcp
   ```

### Optional

4. **Repomix** (for 77% token reduction):
   ```bash
   npm install -g repomix
   ```

---

## Usage

### From Slash Command (Recommended)

```bash
# Claude analyzes EPIC, generates repomap, uploads, then interacts
/chatgpt-implement EPIC-025

# Override scope
/chatgpt-implement EPIC-025 --scope=fullstack-review
```

### Direct Helper Usage

```bash
# Generate repomap and upload
python3 tools/chatgpt_upload_helper.py --scope fullstack-review

# Upload specific files
python3 tools/chatgpt_upload_helper.py --files repomap.txt spec.md

# Custom MCP server URL
python3 tools/chatgpt_upload_helper.py --scope backend --mcp-url http://localhost:8931/mcp
```

**What happens:**
1. Helper generates repomap (if --scope provided)
2. Opens ChatGPT in browser
3. Authenticates if needed (pauses for 2FA)
4. Uploads files
5. Prints: "✅ Setup complete! Claude will now take over..."
6. Claude continues with intelligent interaction

---

## Workflow Example

### Step 1: User Runs Command

```bash
/chatgpt-implement EPIC-025
```

### Step 2: Helper Automates Setup

```
🚀 ChatGPT Upload Helper
   MCP Server: http://localhost:8931/mcp

🔌 Connecting to Playwright MCP...
   ✓ Connected - 24 tools available

📊 Generating repomap (scope: fullstack-review)...
   ✓ Generated: repomaps/20251101_120000/repomap-fullstack-review.txt
   ✓ Including MASTER_SPEC.md

🌐 Opening ChatGPT...
   ✓ Already authenticated

📤 Uploading 2 file(s)...
   → repomap-fullstack-review.txt (2.15 MB)
   → MASTER_SPEC.md (45.2 KB)
   ✓ Files uploaded

✅ Setup complete! Claude will now take over for:
   - Generating and sending contextual prompt
   - Monitoring response completion
   - Extracting and applying patches
```

### Step 3: Claude Takes Over

**Claude analyzes EPIC:**
```
EPIC-025: Async Email Processing

Domain: Backend
Requirements:
1. Create async email queue worker
2. Implement exponential backoff
3. Add database migration
4. Comprehensive error handling
5. Unit tests
```

**Claude generates contextual prompt:**
```
EPIC-025: Async Email Processing

Objective: Implement asynchronous email queue with retry logic

Context:
- Project uses FastAPI async/await patterns
- Email service in src/services/email.py
- PostgreSQL with Alembic migrations
- Celery for background tasks

Requirements:
[... detailed requirements ...]

Focus Areas:
- Proper async/await usage
- Database transaction boundaries
- Error recovery patterns from existing services

Output Format:
Unified diff patches (git apply compatible):
- EPIC-025-01-database-schema.patch
- EPIC-025-02-email-queue.patch
- EPIC-025-03-tests.patch
```

**Claude sends prompt via MCP:**
```python
# Take snapshot to find textarea
snapshot = mcp__playwright__browser_snapshot()

# Find message input ref
textarea_ref = extract_textarea_ref(snapshot)

# Send prompt
mcp__playwright__browser_type(
    element="message textarea",
    ref=textarea_ref,
    text=contextual_prompt,
    submit=True
)
```

**Claude monitors completion:**
```python
while not complete:
    snapshot = mcp__playwright__browser_snapshot()
    if "Regenerate" in snapshot and "Stop generating" not in snapshot:
        complete = True
    await sleep(15)
```

**Claude extracts patches:**
```python
# Get final response
snapshot = mcp__playwright__browser_snapshot()

# Parse response text from accessibility tree
response_text = extract_text_from_snapshot(snapshot)

# Find diff blocks
patches = extract_patches_from_text(response_text)

# Save each patch
for i, patch in enumerate(patches):
    filename = f"EPIC-025-{i+1:02d}-{patch.description}.patch"
    write_file(filename, patch.content)
```

**Claude applies patches:**
```bash
git apply --check EPIC-025-01-database-schema.patch
git apply EPIC-025-01-database-schema.patch
git apply EPIC-025-02-email-queue.patch
git apply EPIC-025-03-tests.patch

git status
```

**Claude validates and reports:**
```
✅ EPIC-025 Implementation Complete

Patches Applied:
- EPIC-025-01-database-schema.patch
- EPIC-025-02-email-queue.patch
- EPIC-025-03-tests.patch

Files Changed:
M  src/models/email_queue.py (new)
M  src/services/email.py
M  alembic/versions/abc123_add_email_queue.py (new)
A  tests/test_email_queue.py (new)

Next Steps:
1. Review: git diff
2. Test: pytest tests/test_email_queue.py
3. Validate: npm run validate-all
4. Commit: git commit -m "feat: Implement EPIC-025"
```

---

## 2FA Handling

If 2FA is required during authentication:

```
🌐 Opening ChatGPT...
   → Not logged in, attempting authentication...
   → Retrieved credentials for user@example.com
   → Attempting automated login...
   ⏸️  If 2FA is required, complete it manually
   → Claude will resume after you're logged in
   Press Enter when authentication is complete...
```

Just authenticate in browser and press Enter - helper continues automatically.

---

## Error Handling

### MCP Not Available

```
❌ MCP connection error: Connection refused

→ Ensure Playwright MCP is running:
  ~/bin/start-playwright-extension.sh
```

**Fix:**
```bash
ps aux | grep playwright
~/bin/start-playwright-extension.sh
curl http://localhost:8931/mcp  # Should respond
```

### Gopass Not Configured

```
⚠️  Could not retrieve credentials from gopass
→ Please authenticate manually in the browser
Press Enter when logged in...
```

**Fix (for future runs):**
```bash
gopass insert chatgpt_user
gopass insert chatgpt_pw
```

### Upload Failed

```
✗ Upload error: File not found
```

**Fix:**
- Verify repomap generation succeeded
- Check file paths are absolute
- Ensure files aren't too large (ChatGPT limit: 20MB per file)

### Response Parsing Issues

If Claude has trouble extracting patches:
1. Claude can ask ChatGPT to regenerate in proper format
2. Claude can manually parse response with retry logic
3. User can manually copy patches from browser

---

## Advantages of This Architecture

### vs. Fully Automated Script (Old Approach)

**Old (839 lines, brittle):**
- ❌ Complex state management
- ❌ Brittle response parsing with regex
- ❌ Hardcoded polling intervals
- ❌ Breaks when ChatGPT UI changes
- ❌ No adaptation to unexpected responses

**New (200 lines + Claude's intelligence):**
- ✅ Simple: Just upload files
- ✅ Flexible: Claude adapts to UI changes
- ✅ Intelligent: Claude parses contextually
- ✅ Interactive: Claude can iterate with ChatGPT
- ✅ Maintainable: Less code to break

### Key Benefits

1. **Separation of Concerns:**
   - Script: Dumb automation (upload files)
   - Claude: Intelligent interaction (prompting, parsing, validation)

2. **Adaptability:**
   - ChatGPT UI changes? Claude adapts in real-time
   - Unexpected response format? Claude handles intelligently
   - Need refinement? Claude can iterate

3. **Simplicity:**
   - No complex state management
   - No brittle regex parsing
   - No hardcoded timeouts/intervals

4. **Maintainability:**
   - 200 lines vs 839 lines
   - Clear responsibilities
   - Easy to debug

---

## Scope Selection

Helper auto-includes MASTER_SPEC.md when generating repomap.

**Available scopes:**
- `backend` - Backend code only
- `complete-backend` - Backend + specs + workflow
- `frontend` - Frontend components and pages
- `fullstack-review` - Backend + frontend + specs (comprehensive)
- `review-ready` - Optimized for external AI review

**With Repomix (77% token reduction):**
- `fullstack-review`: ~500K tokens (was 2.3M)
- `complete-backend`: ~400K tokens (was 1.8M)

---

## Tips for Best Results

### 1. Be Specific in Prompts

**Good:**
```
Implement async email queue in src/services/email.py
Follow the async pattern from src/services/notification.py
Use SQLAlchemy async session from src/database/session.py
Add retry logic with exponential backoff (3 retries, 2^n seconds)
```

**Bad:**
```
Add email queue
```

### 2. Request Proper Format

Always request git-compatible unified diff patches:
```
Output Format:
- Unified diff format (git apply compatible)
- One patch per logical component
- Include full file paths
- Preserve indentation
```

### 3. Verify Coverage

Check repomap includes relevant files before uploading:
```bash
python3 tools/generate_scoped_repomap.py --scope backend | grep email
```

### 4. Iterate as Needed

Claude can have multi-turn conversations:
- Ask ChatGPT for refinements
- Request specific improvements
- Clarify ambiguous responses

---

## Troubleshooting

### Helper Script Errors

**Import error:**
```bash
pip install mcp
```

**File not found:**
```bash
# Verify installation
ls -la tools/chatgpt_upload_helper.py

# If missing, deploy tier1 workflow
/tier1-deploy
```

### Claude Interaction Issues

**Can't find textarea:**
- ChatGPT UI changed
- Take snapshot and inspect element refs
- Look for alternative indicators

**Response incomplete:**
- Increase wait time
- Check for "Continue generating" button
- Ask ChatGPT to continue

**Patches don't apply:**
```bash
# Check patch format
file EPIC-025-01-*.patch

# Try dry-run
git apply --check EPIC-025-01-*.patch

# Review errors
git apply EPIC-025-01-*.patch 2>&1 | head -20
```

---

## Future Enhancements

**Potential improvements:**

1. **ChatGPT API Integration:**
   - More reliable than browser automation
   - No UI dependencies
   - Structured responses

2. **Multi-AI Support:**
   - Upload to Gemini, Claude Pro
   - Compare responses
   - Ensemble implementation

3. **Patch Validation:**
   - Automatic syntax checking
   - Test execution before commit
   - Linting integration

4. **Incremental Updates:**
   - Upload only changed files
   - Context-aware prompting
   - Diff-based prompts

---

## Comparison: Old vs New

| Feature | Old (Full Automation) | New (Helper + Claude) |
|---------|----------------------|----------------------|
| **Lines of code** | 839 | 200 |
| **Brittle parsing** | Yes (regex) | No (Claude) |
| **State management** | Complex (.json files) | None needed |
| **UI adaptability** | Breaks on changes | Claude adapts |
| **Response parsing** | Hardcoded patterns | Intelligent extraction |
| **Iteration** | No (one-shot) | Yes (multi-turn) |
| **Error recovery** | Limited | Intelligent retry |
| **Maintenance** | High | Low |

---

**Last Updated**: 2025-11-01
**Status**: Production Ready
**Architecture**: Simple Helper + Claude Intelligence
