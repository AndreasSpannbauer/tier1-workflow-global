---
description: "Generate scoped repomap for specific PR changed files and dependencies"
allowed-tools: [Bash(./scripts/generate_pr_repomap.sh:*), Bash(gh pr view:*), Bash(ls -lh workspace/pr-exports/*:*), Bash(cat workspace/pr-exports/*:*), AskUserQuestion, Read]
argument-hint: "<PR_NUMBER> [output_file]"
---

## Instructions

Generate a focused repomap for a specific Pull Request, including changed files, their dependencies, and reverse dependencies.

### Step 1: Parse Arguments

**If PR number provided in $ARGUMENTS:**
- Extract PR number from arguments
- Skip to Step 2

**If no arguments provided:**
- Use `AskUserQuestion` to ask for PR number:
  - **Question:** "Which PR would you like to generate a repomap for?"
  - **Header:** "PR Number"
  - **Options:** (User will provide custom input via "Other")

### Step 2: Verify PR Exists

**Check if PR is valid:**
```bash
gh pr view <PR_NUMBER> --json number,title,state --jq '.number'
```

**If PR not found:**
- Display error: "PR #{PR_NUMBER} not found in this repository"
- Suggest: `gh pr list` to see available PRs
- Exit with error

**If PR found:**
- Display PR summary: Number, Title, State
- Continue to Step 3

### Step 3: Generate PR Repomap

**Execute PR repomap script:**
```bash
./scripts/generate_pr_repomap.sh <PR_NUMBER>
```

**The script automatically:**
- Fetches changed files from PR via GitHub CLI
- Shows file structure context (tree view)
- Extracts imports/dependencies from code files
- Lists reverse dependencies (files that import changed files)
- Generates summary statistics
- Saves to: `workspace/pr-exports/PR-<PR_NUMBER>-repomap.txt`

**Custom output location (optional):**
```bash
./scripts/generate_pr_repomap.sh <PR_NUMBER> custom/path/output.txt
```

### Step 4: Display Results

**Show repomap location and stats:**
```bash
ls -lh workspace/pr-exports/PR-<PR_NUMBER>-repomap.txt
```

**Display summary:**
- Output file path
- File size
- Number of lines
- Number of changed files

**Provide usage instructions:**
- "Repomap saved to: `workspace/pr-exports/PR-<PR_NUMBER>-repomap.txt`"
- "View: `cat workspace/pr-exports/PR-<PR_NUMBER>-repomap.txt`"
- "Copy to clipboard: `xclip -selection clipboard < workspace/pr-exports/PR-<PR_NUMBER>-repomap.txt`"
- "Use for PR review context or external AI review"

### Step 5: Offer Next Actions

Use `AskUserQuestion` to offer:
- **Question:** "What would you like to do with the PR repomap?"
- **Options:**
  - "View repomap content" (run `cat workspace/pr-exports/PR-<PR_NUMBER>-repomap.txt`)
  - "Copy to clipboard" (run xclip command)
  - "Generate another PR repomap" (restart from Step 1)
  - "Done" (exit)

## Notes

- **PR repomap structure:**
  - Changed files with addition/deletion counts
  - File tree context for each changed file
  - Imports/dependencies (Python, TypeScript, JavaScript)
  - Function/class structure overview
  - Reverse dependencies (files that import changed files)
  - Summary statistics

- **Output directory:** `workspace/pr-exports/` (auto-created if missing)

- **Supported file types:**
  - Python (`.py`): Shows imports, classes, functions
  - TypeScript (`.ts`, `.tsx`): Shows imports, interfaces, types, functions
  - JavaScript (`.js`, `.jsx`): Shows imports, functions

- **Use cases:**
  - PR review preparation
  - External AI review (ChatGPT, Gemini)
  - Understanding PR impact and dependencies
  - Change context for code review

- **Integration with other tools:**
  - Use with `/chatgpt-implement` for ChatGPT review
  - Complement to full repomap (`/generate-repomap`)
  - Works with GitHub CLI (`gh` command required)

## Troubleshooting

**If script not found:**
```
Error: ./scripts/generate_pr_repomap.sh not found

Solution:
1. Create scripts/generate_pr_repomap.sh (see tier1 workflow reference)
2. Make executable: chmod +x scripts/generate_pr_repomap.sh
3. Verify GitHub CLI installed: gh --version
```

**If GitHub CLI not authenticated:**
```
Error: gh pr view failed (not authenticated)

Solution:
1. Authenticate GitHub CLI: gh auth login
2. Verify authentication: gh auth status
3. Retry PR repomap generation
```

**If output directory creation fails:**
```
Error: Cannot create workspace/pr-exports/

Solution:
1. Check permissions: ls -ld workspace/
2. Create manually: mkdir -p workspace/pr-exports
3. Retry PR repomap generation
```

**If PR has no changed files:**
```
Error: No changed files found in PR #<PR_NUMBER>

Possible causes:
- PR is empty or draft
- PR was closed without changes
- GitHub API issue

Solution:
1. Verify PR exists: gh pr view <PR_NUMBER>
2. Check PR has commits: gh pr view <PR_NUMBER> --json commits
3. Try different PR number
```

## Example Output

```
Generating scoped repomap for PR #123...

Changed files: src/services/user.py tests/test_user.py

✓ Repomap generated: workspace/pr-exports/PR-123-repomap.txt
  Size: 156 lines

Summary:
- Changed files: 2
- Imports analyzed: 15
- Reverse dependencies: 3
- PR URL: https://github.com/owner/repo/pull/123

Next steps:
1. View: cat workspace/pr-exports/PR-123-repomap.txt
2. Copy to clipboard for external review
3. Use for ChatGPT/Gemini PR analysis
```
