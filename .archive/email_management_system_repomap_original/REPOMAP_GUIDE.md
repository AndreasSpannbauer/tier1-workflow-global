# Scoped Repository Map Generator Guide

## Overview

Generate focused repository maps for efficient external review (ChatGPT, Gemini, etc.) without overwhelming them with the entire codebase.

## Quick Start

```bash
# List available scopes
python3 tools/generate_scoped_repomap.py --list-scopes

# Generate review-ready map (most common)
python3 tools/generate_scoped_repomap.py --scope review-ready

# Generate backend-focused map
python3 tools/generate_scoped_repomap.py --scope backend

# Combine multiple scopes
python3 tools/generate_scoped_repomap.py --scopes workflow specs backend
```

## Available Scopes

### Single Scopes

**`backend`** - Backend Python code
- FastAPI services, models, database
- Tests
- Alembic migrations
- ~100KB max file size
- **Use for:** Backend architecture review, service layer analysis

**`workflow`** - V6 workflow and task management
- .tasks/ directory (specs, tasks, plans)
- .claude/ commands and config
- Workflow utilities
- ~200KB max file size
- **Use for:** Workflow system review, epic/task structure

**`specs`** - Specifications and documentation
- Epic specifications
- Architecture docs
- ADRs and references
- CLAUDE.md, README.md
- ~300KB max file size
- **Use for:** High-level architecture review, documentation check

**`frontend`** - Frontend React/TypeScript
- React components
- TypeScript code
- Vite config
- ~100KB max file size
- **Use for:** Frontend architecture review

**`infrastructure`** - Deployment and DevOps
- Docker files
- GitHub Actions
- Deployment scripts
- ~50KB max file size
- **Use for:** Infrastructure review, CI/CD analysis

**`chatgpt-integration`** - ChatGPT integration system
- Templates and tools
- Integration guides
- Commands
- ~100KB max file size
- **Use for:** ChatGPT workflow review

**`complete-backend`** - Complete backend view
- Backend code + specs + workflow
- Comprehensive view for deep review
- ~150KB max file size
- **Use for:** Complete backend architecture assessment

**`review-ready`** - Optimized for external review
- Most relevant files for ChatGPT/Gemini
- CLAUDE.md, specs, core services
- Test coverage
- ~100KB max file size
- **Use for:** Quick external review, getting feedback

**`claude-sdk-integration`** - Complete Claude Agent SDK integration context
- **Comprehensive view including:**
  - Core: claude_workspace, lib, tools, ops, src, scripts
  - Task management: .tasks, .specs
  - Documentation: docs/prompts, obsidian-plugin
  - Infrastructure: migrations, monitoring, contracts, config, alembic
  - Testing: tests/** (all test files)
  - CI/CD: .github/workflows/**
  - Frontend: frontend/, web/, app/, ui/ (TS/TSX/JS/JSX + public/)
  - Build: Taskfile.yml, Makefile
  - Project root: CLAUDE.md, README.md, pyproject.toml, docker-compose, etc.
- **2,021 files, ~21.64 MB**
- ~500KB max file size per file (3 large files excluded)
- **⚠️ Size notice:** Exceeds ChatGPT 20MB text limit by 1.64 MB
- **Solutions:**
  - **Recommended:** Convert to PDF (ChatGPT supports up to 512MB PDF)
  - **Alternative:** Use Gemini 1.5 Pro (1M tokens = ~250MB)
  - **Fallback:** Generate smaller focused scopes
- **Use for:** Most comprehensive system review, full-stack architecture assessment, ChatGPT/Gemini feedback on entire codebase

### Scope Combinations

**`full-review`** - Comprehensive external review
- Combines: specs + workflow + backend
- Max 5MB total
- **Use for:** Comprehensive project review

**`epic-context`** - Epic implementation context
- Combines: specs + backend
- Max 3MB total
- **Use for:** Getting feedback on specific epic implementation

## Usage Examples

### Example 1: Quick Project Review

```bash
# Generate review-ready map for ChatGPT
python3 tools/generate_scoped_repomap.py --scope review-ready --output /tmp/review.txt

# Copy to clipboard (Linux)
xclip -selection clipboard < /tmp/review.txt

# Or view file
cat /tmp/review.txt
```

Then paste into ChatGPT with:
```
I need you to review this codebase. Here's a focused repository map showing the most important files. Please analyze:
1. Architecture patterns and quality
2. Potential issues or improvements
3. Code organization and structure
4. Best practices compliance

[PASTE REPOMAP]
```

### Example 2: Backend Architecture Review

```bash
# Generate complete backend view
python3 tools/generate_scoped_repomap.py --scope complete-backend

# The output filename includes timestamp
# Example: repomap-complete-backend-20250130_091508.txt
```

Prompt for ChatGPT:
```
Review this backend architecture. Focus on:
- Service layer boundaries
- Async/await patterns
- Database interaction patterns
- Error handling
- Test coverage

[PASTE REPOMAP]
```

### Example 3: Workflow System Review

```bash
# Generate workflow-focused map
python3 tools/generate_scoped_repomap.py --scope workflow

# Add custom patterns
python3 tools/generate_scoped_repomap.py \
    --scope workflow \
    --include "tools/chatgpt_integration/**/*.py"
```

### Example 4: Multiple Scopes Combined

```bash
# Combine specs + backend for epic review
python3 tools/generate_scoped_repomap.py --scopes specs backend

# Full review combination
python3 tools/generate_scoped_repomap.py --scope full-review
```

### Example 5: Claude Agent SDK Integration Review

```bash
# Generate comprehensive Claude SDK integration map
./tools/quick_repomap.sh claude-sdk

# Or with full command
python3 tools/generate_scoped_repomap.py \
    --scope claude-sdk-integration \
    --output docs/prompts/chatgpt/repomap-claude-sdk.txt \
    --stats

# Output: 2,021 files, 21.64 MB
# Includes: claude_workspace, lib, tools, ops, src, scripts, .tasks, .specs,
#           docs/prompts, obsidian-plugin, migrations, monitoring, contracts,
#           config, alembic, tests, .github/workflows, frontend, and project root

# ⚠️ File is 21.64 MB (exceeds 20MB text limit by 1.64 MB)
# Solution: Convert to PDF for ChatGPT

# Convert to PDF (requires pandoc and LaTeX)
pandoc docs/prompts/chatgpt/repomap-claude-sdk.txt \
    -o docs/prompts/chatgpt/repomap-claude-sdk.pdf \
    --pdf-engine=pdflatex

# Upload PDF to ChatGPT (supports up to 512MB)

# Or for Gemini 1.5 Pro (1M tokens, can handle 21.64 MB text directly)
cat docs/prompts/chatgpt/repomap-claude-sdk.txt
# Copy and paste
```

Then paste into ChatGPT with:
```
I need comprehensive review of our Claude Agent SDK integration and system architecture.
This repomap includes our complete codebase structure. Please analyze:

1. Claude Agent SDK integration patterns and correctness
2. Architecture quality and adherence to best practices
3. Code organization and maintainability
4. Potential issues, improvements, and optimizations
5. Documentation completeness and clarity
6. Testing strategy and coverage

Focus on the following areas:
- Backend FastAPI services and async patterns
- Claude Agent SDK authentication and usage
- MCP tools integration (in-process server pattern)
- Task/workflow management system
- Database migrations and schema design

[PASTE REPOMAP]
```

### Example 6: Custom Scope

```bash
# Create custom scope with specific patterns
python3 tools/generate_scoped_repomap.py \
    --include "src/services/**/*.py" \
    --include "tests/services/**/*.py" \
    --include "docs/architecture/**/*.md" \
    --exclude "**/__pycache__/**" \
    --max-file-size 150000 \
    --output /tmp/custom-review.txt
```

## Configuration

Scopes are defined in `tools/repomap_scopes.json`. You can:
- Add new scopes
- Modify existing patterns
- Create new combinations
- Adjust file size limits

Example scope definition:
```json
{
  "scopes": {
    "my-scope": {
      "description": "My custom scope",
      "include_patterns": [
        "src/**/*.py",
        "docs/**/*.md"
      ],
      "exclude_patterns": [
        "**/__pycache__/**"
      ],
      "max_file_size": 100000
    }
  }
}
```

## Output Format

Generated repomap includes:
- Metadata header (timestamp, scope info, file count, size)
- Include/exclude patterns used
- Each file with its path and size
- Full content of each file

Example header:
```
# Scoped Repository Map
# Generated: 2025-10-30T09:15:08.611749+00:00
# Scope: review-ready
# Files included: 195
# Total size: 2,738,374 bytes (2.61 MB)
```

## Tips for External Review

### ChatGPT Prompts

**Architecture Review:**
```
Review this codebase architecture. Analyze:
1. Separation of concerns
2. Design patterns used
3. Code organization
4. Potential issues
5. Suggestions for improvement

Focus on Python backend with FastAPI.

[PASTE REPOMAP]
```

**Epic Implementation Feedback:**
```
I'm implementing EPIC-023: Drop Legacy Database Tables.
Review the current specification and codebase structure.
Suggest improvements for:
- Safety checks
- Test coverage
- Error handling
- Documentation

[PASTE REPOMAP]
```

**Workflow System Review:**
```
Review our V6 workflow system. Evaluate:
- Epic/task structure
- Automation effectiveness
- Documentation clarity
- Integration with tools

[PASTE REPOMAP]
```

### Gemini Prompts

Similar approach, but Gemini can handle larger contexts:
```bash
# Generate larger scope for Gemini
python3 tools/generate_scoped_repomap.py --scope full-review
```

### Token Management

**Size estimates:**
- `review-ready`: ~2.6 MB (~650K tokens)
- `backend`: ~1-2 MB (~250-500K tokens)
- `workflow`: ~500KB-1MB (~125-250K tokens)
- `specs`: ~300-600KB (~75-150K tokens)

**ChatGPT limits:**
- GPT-4: 8K-32K tokens (use smaller scopes)
- GPT-4-turbo: 128K tokens (can handle review-ready)

**Gemini limits:**
- Gemini 1.5 Pro: 1M tokens (can handle full-review)

## Best Practices

1. **Start small**: Use `review-ready` for quick feedback
2. **Be specific**: Choose scopes matching your question
3. **Combine wisely**: Multiple scopes increase size quickly
4. **Check size**: Use `--stats` to see what's included
5. **Iterate**: Get feedback, adjust scope, regenerate

## Troubleshooting

**Output too large:**
```bash
# Check what's included
python3 tools/generate_scoped_repomap.py --scope backend --stats

# Reduce max file size
python3 tools/generate_scoped_repomap.py --scope backend --max-file-size 50000

# Use smaller scope
python3 tools/generate_scoped_repomap.py --scope specs
```

**Missing files:**
```bash
# Check scope patterns
python3 tools/generate_scoped_repomap.py --list-scopes

# Add custom include
python3 tools/generate_scoped_repomap.py --scope backend --include "path/to/file.py"
```

**Pattern not working:**
- Patterns are git-tracked files only
- Use glob syntax: `**/*.py` for recursive, `src/*.py` for single level
- Exclude patterns override include patterns

## Integration with ChatGPT Workflow

Combined with ChatGPT integration system:

```bash
# 1. Generate focused repomap
python3 tools/generate_scoped_repomap.py --scope review-ready -o /tmp/repo.txt

# 2. Generate epic review prompt
/chatgpt-integrate review-epic EPIC-023

# 3. Combine in ChatGPT:
#    - Paste epic review prompt
#    - Add: "Context - here's the relevant codebase:"
#    - Paste repomap

# 4. Get comprehensive feedback on both spec and implementation
```

## Future Enhancements

- [ ] Automatic token estimation
- [ ] Smart scope selection based on question
- [ ] Incremental updates (only changed files)
- [ ] Integration with ChatGPT API
- [ ] Web UI for scope selection
- [ ] Diff-based repomaps (only show changes)

## Support

For issues or questions:
1. Check scope patterns in `tools/repomap_scopes.json`
2. Use `--stats` to debug inclusion/exclusion
3. Test with `--list-scopes` first
4. Start with small scopes and expand

---

**Last Updated:** 2025-10-30
**Version:** 1.0.0
**Status:** Production Ready
