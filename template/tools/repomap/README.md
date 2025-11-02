# Scoped Repository Map Generator

## Overview

Generate focused repository maps for efficient external review (ChatGPT, Gemini, etc.) without overwhelming them with the entire codebase.

Automatically detects project type and generates both TXT and optimized PDF outputs in timestamped directories.

## Quick Start

```bash
# List available scopes
python3 tools/repomap/generate_repomap.py --list-scopes

# Auto-detect project type and generate appropriate repomap
python3 tools/repomap/generate_repomap.py --auto-detect

# Generate review-ready map (most common)
python3 tools/repomap/generate_repomap.py --scope review-ready

# Generate backend-focused map
python3 tools/repomap/generate_repomap.py --scope backend

# Combine multiple scopes
python3 tools/repomap/generate_repomap.py --scopes backend workflow
```

## Features

- **Auto-detection**: Automatically detects project type (backend, frontend, fullstack, workflow)
- **Scoped generation**: Focus on specific parts of your codebase
- **Multiple output formats**: TXT + PDF generation with automatic compression
- **Timestamped outputs**: `repomaps/YYYYMMDD_HHMMSS/` directory structure
- **Size validation**: Ensures outputs are <20MB for ChatGPT
- **Statistics**: File count, size reporting, exclusion tracking
- **Custom scopes**: Project-specific overrides via `repomap_scopes_custom.json`

## Available Scopes

### Single Scopes

**`backend`** - Backend code
- Python, TypeScript, Go, Rust
- Tests, migrations, requirements
- ~100KB max file size
- **Use for:** Backend architecture review, service layer analysis

**`frontend`** - Frontend code
- React, Vue, Next.js, etc.
- TypeScript/JavaScript, CSS
- Config files (vite, next, tailwind)
- ~100KB max file size
- **Use for:** Frontend architecture review

**`workflow`** - Tier1 workflow and task management
- .tasks/ directory (specs, tasks, plans)
- .claude/ commands and config
- Tools and scripts
- ~200KB max file size
- **Use for:** Workflow system review, epic/task structure

**`specs`** - Specifications and documentation
- Epic specifications
- Architecture docs, ADRs
- CLAUDE.md, README.md
- ~300KB max file size
- **Use for:** High-level architecture review

**`infrastructure`** - Deployment and DevOps
- Docker files
- GitHub Actions, GitLab CI
- Kubernetes, Terraform, Ansible
- ~50KB max file size
- **Use for:** Infrastructure review, CI/CD analysis

**`tests`** - Test files
- Python tests (pytest)
- JavaScript/TypeScript tests (jest, vitest)
- Test configs
- ~100KB max file size
- **Use for:** Test coverage analysis

**`complete-backend`** - Complete backend view
- Backend code + specs + workflow
- Comprehensive view for deep review
- ~150KB max file size

**`complete-frontend`** - Complete frontend view
- Frontend code + specs + workflow
- Comprehensive view for deep review
- ~150KB max file size

**`review-ready`** - Optimized for external review
- Most relevant files for ChatGPT/Gemini
- CLAUDE.md, specs, core services
- Test coverage
- ~100KB max file size
- **Use for:** Quick external review, getting feedback

**`generic`** - Generic project overview
- README, docs, src, lib
- Package manifests
- ~100KB max file size
- **Use for:** Projects without clear backend/frontend structure

### Scope Combinations

**`full-review`** - Comprehensive external review
- Combines: specs + workflow + backend
- Max 5MB total

**`fullstack-review`** - Complete fullstack project review
- Combines: specs + backend + frontend
- Max 5MB total

**`epic-context`** - Epic implementation context
- Combines: specs + backend
- Max 3MB total

**`deployment-ready`** - Infrastructure context
- Combines: infrastructure + specs
- Max 2MB total

## Usage Examples

### Example 1: Auto-Detect Project Type

```bash
# Let the tool detect your project type and select appropriate scope
python3 tools/repomap/generate_repomap.py --auto-detect
```

**Detection logic:**
- **Backend**: Python, Go, Rust files in `src/`, `api/`, `server/`
- **Frontend**: React/Vue files in `frontend/`, `src/`, `components/`
- **Fullstack**: Both backend and frontend files detected
- **Workflow**: Tier1 workflow files (`.tasks/`, `.claude/`, `CLAUDE.md`)

### Example 2: Quick Project Review

```bash
# Generate review-ready map for ChatGPT
python3 tools/repomap/generate_repomap.py --scope review-ready

# Output: repomaps/20251101_103000/repomap-review-ready.txt
#         repomaps/20251101_103000/repomap-review-ready.pdf
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

### Example 3: Backend Architecture Review

```bash
# Generate complete backend view
python3 tools/repomap/generate_repomap.py --scope complete-backend
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

### Example 4: Multiple Scopes Combined

```bash
# Combine specs + backend for epic review
python3 tools/repomap/generate_repomap.py --scopes specs backend

# Full review combination
python3 tools/repomap/generate_repomap.py --scope full-review
```

### Example 5: Custom Patterns

```bash
# Create custom scope with specific patterns
python3 tools/repomap/generate_repomap.py \
    --include "src/services/**/*.py" \
    --include "tests/services/**/*.py" \
    --include "docs/architecture/**/*.md" \
    --exclude "**/__pycache__/**" \
    --max-file-size 150000
```

### Example 6: PR-Specific Repomap

```bash
# Generate repomap for PR changed files
./scripts/generate_pr_repomap.sh 123

# Custom output location
./scripts/generate_pr_repomap.sh 123 /tmp/pr-123-review.txt
```

## Configuration

### Default Scopes

Scopes are defined in `tools/repomap/repomap_scopes.json`.

### Project-Specific Overrides

Create `tools/repomap_scopes_custom.json` in your project to override or add scopes:

```json
{
  "scopes": {
    "my-custom-scope": {
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

Custom scopes take precedence over default scopes.

### Scope Structure

```json
{
  "scopes": {
    "scope-name": {
      "description": "Scope description",
      "include_patterns": [
        "path/**/*.ext",
        "specific/file.py"
      ],
      "exclude_patterns": [
        "**/__pycache__/**",
        "**/node_modules/**"
      ],
      "max_file_size": 100000
    }
  },
  "scope_combinations": {
    "combination-name": {
      "description": "Combination description",
      "scopes": ["scope1", "scope2"],
      "max_total_size": 5000000
    }
  }
}
```

## Output Format

### Directory Structure

```
repomaps/
└── 20251101_103000/
    ├── repomap-backend.txt
    └── repomap-backend.pdf
```

### File Header

```
# Scoped Repository Map
# Generated: 2025-11-01T10:30:00.123456+00:00
# Root: /path/to/project
# Scope: backend
# Description: Backend code (Python, TypeScript, Go, etc.)
# Files included: 195
# Total size: 2,738,374 bytes (2.61 MB)
# Max file size: 100000 bytes

# Include patterns:
#   - src/**/*.py
#   - api/**/*.py
#   ...

# Exclude patterns:
#   - **/__pycache__/**
#   ...

================================================================================

--- File: src/main.py (1234 bytes) ---
[file content]

--- File: src/service.py (5678 bytes) ---
[file content]
```

## Commands Reference

### List Scopes

```bash
python3 tools/repomap/generate_repomap.py --list-scopes
```

### Generate with Specific Scope

```bash
python3 tools/repomap/generate_repomap.py --scope SCOPE_NAME
```

### Auto-Detect Project Type

```bash
python3 tools/repomap/generate_repomap.py --auto-detect
```

### Combine Multiple Scopes

```bash
python3 tools/repomap/generate_repomap.py --scopes scope1 scope2 scope3
```

### Custom Output Path

```bash
python3 tools/repomap/generate_repomap.py --scope backend --output /tmp/review.txt
```

### Skip PDF Generation

```bash
python3 tools/repomap/generate_repomap.py --scope backend --no-pdf
```

### Show Statistics

```bash
python3 tools/repomap/generate_repomap.py --scope backend --stats
```

### Custom Config File

```bash
python3 tools/repomap/generate_repomap.py --scope backend --config /path/to/config.json
```

### Override Max File Size

```bash
python3 tools/repomap/generate_repomap.py --scope backend --max-file-size 200000
```

### Cleanup Old Repomaps

```bash
# Interactive cleanup
./tools/repomap/cleanup_repomaps.sh

# Force cleanup without confirmation
./tools/repomap/cleanup_repomaps.sh --force
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

Focus on [Python backend with FastAPI / React frontend / etc.].

[PASTE REPOMAP]
```

**Epic Implementation Feedback:**
```
I'm implementing EPIC-023: [Epic Title].
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
Review our Tier1 workflow system. Evaluate:
- Epic/task structure
- Automation effectiveness
- Documentation clarity
- Integration with tools

[PASTE REPOMAP]
```

### Token Management

**Size estimates:**
- `review-ready`: ~2-3 MB (~500-750K tokens)
- `backend`: ~1-2 MB (~250-500K tokens)
- `frontend`: ~1-2 MB (~250-500K tokens)
- `workflow`: ~500KB-1MB (~125-250K tokens)
- `specs`: ~300-600KB (~75-150K tokens)

**ChatGPT limits:**
- GPT-4: 8K-32K tokens (use smaller scopes)
- GPT-4-turbo: 128K tokens (can handle review-ready)
- ChatGPT file upload: 20MB text, 512MB PDF

**Gemini limits:**
- Gemini 1.5 Pro: 1M tokens (~250MB, can handle full-review)

**PDF Conversion:**
If text file exceeds 20MB, upload PDF instead (ChatGPT supports up to 512MB PDF).

## Best Practices

1. **Start small**: Use `review-ready` or `--auto-detect` for quick feedback
2. **Be specific**: Choose scopes matching your question
3. **Combine wisely**: Multiple scopes increase size quickly
4. **Check size**: Use `--stats` to see what's included
5. **Iterate**: Get feedback, adjust scope, regenerate
6. **Use custom scopes**: Create project-specific scopes for repeated use
7. **Clean up regularly**: Use `cleanup_repomaps.sh` to remove old files

## Troubleshooting

### Output too large

```bash
# Check what's included
python3 tools/repomap/generate_repomap.py --scope backend --stats

# Reduce max file size
python3 tools/repomap/generate_repomap.py --scope backend --max-file-size 50000

# Use smaller scope
python3 tools/repomap/generate_repomap.py --scope specs
```

### Missing files

```bash
# Check scope patterns
python3 tools/repomap/generate_repomap.py --list-scopes

# Add custom include
python3 tools/repomap/generate_repomap.py --scope backend --include "path/to/file.py"

# Check if file is git-tracked
git ls-files | grep "path/to/file"
```

### Pattern not working

- Patterns match git-tracked files only
- Use glob syntax: `**/*.py` for recursive, `src/*.py` for single level
- Exclude patterns override include patterns
- Use quotes around patterns with wildcards

### PDF generation fails

```bash
# Install required tools
sudo apt-get install enscript ghostscript

# Skip PDF generation
python3 tools/repomap/generate_repomap.py --scope backend --no-pdf
```

### Auto-detection wrong

```bash
# Manually specify scope
python3 tools/repomap/generate_repomap.py --scope backend

# Check what was detected
python3 tools/repomap/generate_repomap.py --auto-detect --stats
```

## Architecture

### Modular Design

- **`generate_repomap.py`**: Main entry point and orchestration
- **`scope_manager.py`**: Scope configuration and project type detection
- **`pdf_generator.py`**: PDF conversion using enscript + ps2pdf

### Config File Search Order

1. `--config` argument (if provided)
2. `tools/repomap_scopes_custom.json` (project-specific)
3. `tools/repomap_scopes.json` (project-specific)
4. `tools/repomap/repomap_scopes.json` (tier1 global)
5. Script directory (fallback)

### Project Type Detection

```python
class ProjectTypeDetector:
    def detect(self) -> str:
        has_backend = self._has_backend_files()
        has_frontend = self._has_frontend_files()
        has_workflow = self._has_workflow_files()

        if has_backend and has_frontend:
            return "fullstack"
        elif has_backend:
            return "backend"
        elif has_frontend:
            return "frontend"
        elif has_workflow:
            return "workflow"
        else:
            return "generic"
```

## Integration with Tier1 Workflow

### Deployment

This tooling is deployed via Tier1 workflow to all registered projects:

```bash
# Deploy to specific project
/tier1-deploy --project email_management_system --template repomap

# Deploy to all projects
/tier1-update-all --template repomap
```

### Custom Scopes per Project

Each project can override or extend scopes by creating:
- `tools/repomap_scopes_custom.json` (highest priority)
- `tools/repomap_scopes.json` (project-specific)

## Support

For issues or questions:
1. Check scope patterns: `python3 tools/repomap/generate_repomap.py --list-scopes`
2. Use `--stats` to debug inclusion/exclusion
3. Test with `--auto-detect` first
4. Start with small scopes and expand
5. Check git tracking: `git ls-files`

## Version History

- **v1.0.0** (2025-11-01): Initial tier1 global release
  - Extracted from email_management_system
  - Added auto-detection
  - Added modular architecture
  - Added universal scope definitions
  - Removed project-specific patterns

---

**Status:** Production Ready
**Tier1 Integration:** Yes
**Testing:** Validated in email_management_system
