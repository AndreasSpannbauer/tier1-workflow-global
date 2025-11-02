---
description: "Generate contextual ChatGPT prompts and automate repomap upload/response handling"
allowed-tools: [Bash(python3 tools/chatgpt_repomap_automation.py:*), Bash(python3 tools/generate_scoped_repomap.py:*), Bash(mkdir:*), Bash(cp:*), Bash(ls:*), Bash(find:*), Bash(mv:*), Bash(git apply:*), Read, Write]
argument-hint: "EPIC-ID [--scope=backend|complete-backend|frontend] [--auto]"
---

Generate intelligent, contextual prompts for ChatGPT code implementation requests. Claude analyzes the EPIC and generates focused prompts; the automation script handles browser automation (upload → wait → download).

## Context
- Current working directory: !`pwd`
- Available EPIC: !`ls -1 .tasks/backlog/ | grep EPIC`
- Automation script: `tools/chatgpt_repomap_automation.py`
- Response saved to: `chatgpt-response.json`

## Architecture: Separation of Concerns

**Claude (intelligent):**
- Analyze EPIC context and requirements
- Generate focused, contextual prompts
- Parse ChatGPT response
- Extract and apply patches

**Script (dumb automation):**
- Upload repomap and files to ChatGPT
- Poll for response completion
- Download response JSON
- Handle browser navigation

## Your Task

1. **Parse Arguments**
   - Extract EPIC-ID from $ARGUMENTS
   - Detect --auto flag for automation
   - Detect scope from EPIC domain (default: backend)
   - EPIC format: EPIC-XXX-ShortName

2. **Read and Analyze EPIC**
   - Read `.tasks/backlog/EPIC-{ID}-{Name}/spec.md`
   - Identify domain, objective, requirements, and acceptance criteria
   - Determine appropriate scope: backend, complete-backend, or frontend

3. **Generate Scoped Repomap**
   - Run: `python3 tools/generate_scoped_repomap.py --scope {detected-scope}`
   - Output location: `repomaps/repomap-{scope}.txt`

4. **Generate Intelligent, Contextual Prompt**
   - Analyze EPIC requirements and context
   - Create focused implementation prompt emphasizing:
     - Key architectural decisions
     - Specific patterns to follow (from existing codebase)
     - Testing requirements and edge cases
     - Patch format requirements (unified diff, git apply compatible)
   - Example prompt structure:
     ```
     EPIC-025: Async Email Processing

     Objective: Implement asynchronous email queue with retry logic

     Context:
     - Project uses FastAPI async/await patterns
     - Email service is in src/services/email.py
     - Tasks stored in PostgreSQL with Alembic migrations

     Requirements:
     1. Create async email queue worker
     2. Implement exponential backoff for retries
     3. Add database schema migration
     4. Include comprehensive error handling
     5. Add unit tests for failure scenarios

     Focus Areas:
     - Proper async/await usage throughout
     - Database transaction boundaries
     - Error recovery and logging

     Output Format:
     Generate as unified diff patches compatible with 'git apply':
     - EPIC-025-01-models.patch (database schema)
     - EPIC-025-02-service.patch (email queue implementation)
     - EPIC-025-03-tests.patch (unit tests)
     ```

5. **Call Automation Script with Prompt (--auto mode)**
   ```bash
   echo "$PROMPT" | python3 tools/chatgpt_repomap_automation.py \
     --scope {detected-scope} \
     --timeout 600 \
     --no-resume
   ```
   - Script handles: upload repomap, send prompt, poll, download response
   - Response saved to `chatgpt-response.json`
   - Returns with JSON containing patches, analysis, code blocks

6. **Parse Response and Extract Patches**
   - Load `chatgpt-response.json`
   - Extract patch section (if embedded in response text)
   - Locate downloadable patch files (should be in response)
   - Save patches to project root with naming: `EPIC-{ID}-01-*.patch`

7. **Apply Patches**
   ```bash
   for patch in EPIC-{ID}-*.patch; do
     git apply "$patch" || (echo "Failed: $patch"; exit 1)
   done
   ```
   - Verify with `git status`
   - Check diff with `git diff`

8. **Validate Application**
   - Run project validation suite
   - Run tests if available
   - Check for any syntax errors

9. **Display Summary**
   - List all applied patches
   - Show changed files
   - Report applied EPIC
   - Suggest next steps (review, commit)

## Scope Detection Logic
- **Database** domain → `backend` scope (Alembic, migrations, DB tests)
- **Backend** domain → `complete-backend` scope (full backend context)
- **Frontend** domain → `frontend` scope (React, TypeScript, components)
- **Testing** domain → `backend` scope (test infrastructure)
- **DevOps** domain → `infrastructure` scope (Docker, CI/CD)

## Reference File Selection by Domain
- **Database**: Latest migration files, DB test examples
- **Backend**: Service patterns, API examples, recent implementations
- **Frontend**: Component examples, type definitions, hooks
- **Testing**: Test patterns, fixtures, conftest.py

## Output Format

### Standard Output

```
EPIC Implementation Assistant

EPIC: EPIC-{ID} - {Title}
Domain: {Domain}
Scope: {detected-scope}

Step 1: Generated Repomap
  Location: repomaps/repomap-{scope}.txt
  Size: {size} KB

Step 2: Generated Contextual Prompt
  Focuses on:
  - Architectural patterns from your codebase
  - Specific requirements from EPIC specification
  - Testing and edge case coverage
  - Patch format requirements

Step 3: Sending to ChatGPT via Automation Script
  python3 tools/chatgpt_repomap_automation.py --scope {scope}
  - Uploading repomap + MASTER_SPEC.md
  - Sending contextual prompt
  - Polling for response (max 10 minutes)
  - Downloading response JSON

Step 4: Parsing Response
  Response file: chatgpt-response.json
  Contains: patches, analysis, code blocks

Step 5: Applying Patches
  git apply EPIC-{ID}-01-*.patch
  git apply EPIC-{ID}-02-*.patch
  ... (as generated)

Summary
  Patches applied: {count}
  Files changed: {count}

  Changed files:
    M  src/services/component.py
    M  tests/test_component.py
    M  docs/api.md

Next Steps:
  1. Review changes: git diff
  2. Run tests: npm run test
  3. Validate: npm run validate-all
  4. Commit: git add . && git commit -m "feat: Implement EPIC-{ID}"
```

## Error Handling

### EPIC Not Found
```
List available EPICs:
  ls -1 .tasks/backlog/ | grep EPIC
```

### Repomap Generation Failed
```
Troubleshooting:
1. Check scope name: python3 tools/generate_scoped_repomap.py --list-scopes
2. Verify files exist in src/, api/, frontend/ directories
3. Check disk space: df -h
4. Manually specify scope: generate-repomap backend
```

### Automation Script Errors

**Script not found:**
```
❌ tools/chatgpt_repomap_automation.py not found

Fix:
1. Verify installation: /tier1-deploy or /tier1-update-surgical
2. Check: ls -la tools/chatgpt_repomap_automation.py
```

**Gopass credentials missing:**
```
❌ Failed to retrieve credentials from gopass

Fix:
1. gopass insert chatgpt_user  # Your ChatGPT email
2. gopass insert chatgpt_pw    # Your ChatGPT password
```

**MCP server not available:**
```
❌ Playwright MCP not available

Ensure playwright-mcp service is running:
  ps aux | grep playwright
  curl http://localhost:8931/mcp

Restart:
  systemctl restart playwright-mcp
```

### Response Parsing Errors

**Response file not created:**
```
Check automation script output:
  tail -20 ~/.chatgpt_session_state.json

Verify response was downloaded:
  ls -la chatgpt-response.json
```

**Patches not found in response:**
```
Troubleshooting:
1. Check response structure: python3 -m json.tool chatgpt-response.json
2. Review 'patches' array in response
3. Check 'raw_response' for embedded patch text
4. If patches embedded as text: extract manually and save as .patch files
```

### Patch Application Failed

```
❌ Failed to apply patch: EPIC-{ID}-01-component.patch

Troubleshooting:
1. Verify patch format: file EPIC-{ID}-01-component.patch
2. Check git status: git status
3. Dry-run patch: git apply --check EPIC-{ID}-01-component.patch
4. Review patch content: head -50 EPIC-{ID}-01-component.patch
5. Check for path mismatches in patch headers
6. Ensure target files exist in repository

Manual fix:
  - Edit patch to correct paths
  - Apply manually with: git apply --reject EPIC-{ID}-01-component.patch
  - Review .rej files for conflicts
```
