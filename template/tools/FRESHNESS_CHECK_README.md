# Documentation Freshness Check

Optional tool to track whether documentation is up-to-date with code changes.

## Overview

`check_docs_freshness.py` compares modification timestamps of code files vs documentation files to detect stale documentation. Configurable mapping rules define which docs should be updated when specific code files change.

**Key Features**:
- Configurable file mapping rules (glob patterns)
- Git integration for accurate timestamps
- Warning vs error severity levels
- Multiple output formats (human, JSON)
- CI/CD ready with exit codes
- Smart ignore patterns

## Quick Start

### Generate Default Configuration

```bash
python check_docs_freshness.py --generate-config
```

Creates `.freshness-check.json` with sensible defaults for Python projects.

### Run Check

```bash
# Human-readable report
python check_docs_freshness.py

# JSON output (for CI/CD)
python check_docs_freshness.py --json

# Verbose mode
python check_docs_freshness.py --verbose

# Override threshold
python check_docs_freshness.py --threshold-days 14
```

### Exit Codes

- `0` - All docs fresh or only warnings
- `1` - Stale docs with error severity

## Configuration

### Configuration File

Default: `.freshness-check.json`

```json
{
    "mappings": [
        {
            "code_patterns": ["src/**/*.py"],
            "doc_patterns": ["docs/api/*.md"],
            "threshold_days": 7,
            "severity": "warning"
        },
        {
            "code_patterns": ["src/core/*.py", "src/main.py"],
            "doc_patterns": ["README.md", "docs/getting-started.md"],
            "threshold_days": 3,
            "severity": "error"
        }
    ],
    "ignore_patterns": [
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/vendor/**",
        "**/*.pyc",
        ".git/**"
    ],
    "use_git_timestamps": true
}
```

### Mapping Rules

Each mapping rule defines:

- **`code_patterns`** - Glob patterns for code files (e.g., `["src/**/*.py"]`)
- **`doc_patterns`** - Glob patterns for documentation files (e.g., `["docs/**/*.md"]`)
- **`threshold_days`** - Maximum staleness allowed (e.g., `7`)
- **`severity`** - `"warning"` or `"error"`

**How it works**:
1. Find newest modified code file matching `code_patterns`
2. For each doc file matching `doc_patterns`:
   - Compare code modification time vs doc modification time
   - If difference > `threshold_days`, report as stale

### Severity Levels

- **`warning`** - Reported but doesn't fail CI (exit code 0)
- **`error`** - Fails CI (exit code 1)

Use `error` for critical documentation (README, getting started guides).

### Git Timestamps

When `use_git_timestamps: true`:
- Uses `git log` to get last commit time for each file
- More accurate than filesystem mtime
- Fallback to filesystem if git unavailable

Disable for non-git repos or if git not installed.

## Example Configurations

### Python Project with API Docs

```json
{
    "mappings": [
        {
            "code_patterns": ["src/**/*.py", "*.py"],
            "doc_patterns": ["docs/api/*.md", "README.md"],
            "threshold_days": 7,
            "severity": "warning"
        },
        {
            "code_patterns": ["src/main.py", "src/cli.py"],
            "doc_patterns": ["README.md", "docs/usage.md"],
            "threshold_days": 3,
            "severity": "error"
        }
    ],
    "ignore_patterns": [
        "**/__pycache__/**",
        "**/*.pyc",
        "**/tests/**",
        ".git/**"
    ],
    "use_git_timestamps": true
}
```

### JavaScript/TypeScript Project

```json
{
    "mappings": [
        {
            "code_patterns": ["src/**/*.ts", "src/**/*.tsx"],
            "doc_patterns": ["docs/**/*.md"],
            "threshold_days": 7,
            "severity": "warning"
        },
        {
            "code_patterns": ["src/index.ts", "package.json"],
            "doc_patterns": ["README.md"],
            "threshold_days": 1,
            "severity": "error"
        }
    ],
    "ignore_patterns": [
        "**/node_modules/**",
        "**/dist/**",
        "**/*.test.ts",
        ".git/**"
    ],
    "use_git_timestamps": true
}
```

### Multi-Language Monorepo

```json
{
    "mappings": [
        {
            "code_patterns": ["backend/**/*.py"],
            "doc_patterns": ["docs/backend/**/*.md"],
            "threshold_days": 7,
            "severity": "warning"
        },
        {
            "code_patterns": ["frontend/**/*.tsx", "frontend/**/*.ts"],
            "doc_patterns": ["docs/frontend/**/*.md"],
            "threshold_days": 7,
            "severity": "warning"
        },
        {
            "code_patterns": ["backend/main.py", "frontend/src/App.tsx"],
            "doc_patterns": ["README.md"],
            "threshold_days": 3,
            "severity": "error"
        }
    ],
    "ignore_patterns": [
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/dist/**",
        "**/build/**",
        ".git/**"
    ],
    "use_git_timestamps": true
}
```

## CI/CD Integration

### GitHub Actions

**.github/workflows/docs-freshness.yml**:

```yaml
name: Documentation Freshness Check

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Mondays

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git timestamps

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies (optional)
        run: pip install colorama  # For colored output

      - name: Check documentation freshness
        run: python tools/check_docs_freshness.py --verbose

      - name: Generate JSON report
        if: always()
        run: python tools/check_docs_freshness.py --json > docs-freshness-report.json

      - name: Upload report artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: docs-freshness-report
          path: docs-freshness-report.json
```

### GitLab CI

**.gitlab-ci.yml**:

```yaml
docs-freshness:
  stage: test
  image: python:3.11
  before_script:
    - pip install colorama
  script:
    - python tools/check_docs_freshness.py --verbose
    - python tools/check_docs_freshness.py --json > docs-freshness-report.json
  artifacts:
    when: always
    paths:
      - docs-freshness-report.json
    reports:
      junit: docs-freshness-report.json
  only:
    - merge_requests
    - main
```

### Pre-commit Hook

**.git/hooks/pre-commit**:

```bash
#!/bin/bash
# Check documentation freshness before committing

python tools/check_docs_freshness.py --json > /dev/null 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "⚠️  Warning: Documentation may be stale"
    python tools/check_docs_freshness.py
    echo ""
    echo "Continue commit anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

exit 0
```

Make executable: `chmod +x .git/hooks/pre-commit`

## Usage Examples

### Basic Check

```bash
$ python check_docs_freshness.py

======================================================================
Documentation Freshness Report
======================================================================

Checked: 2 mapping rule(s)
Files: 15 code, 8 docs
Timestamp: 2025-01-15 14:30:00

WARNINGS (2):
  ⚠ docs/api/core.md
    Code changed: 2025-01-10 (src/core/engine.py)
    Doc modified: 2024-12-28
    Staleness: 13 days (threshold: 7)

  ⚠ docs/usage.md
    Code changed: 2025-01-08 (src/cli.py)
    Doc modified: 2024-12-30
    Staleness: 9 days (threshold: 7)

======================================================================
Summary: 0 error(s), 2 warning(s)
======================================================================
```

### JSON Output

```bash
$ python check_docs_freshness.py --json
{
  "check_timestamp": "2025-01-15T14:30:00",
  "is_fresh": false,
  "has_warnings": true,
  "has_errors": false,
  "total_mappings_checked": 2,
  "total_code_files": 15,
  "total_doc_files": 8,
  "stale_docs": [
    {
      "doc_path": "docs/api/core.md",
      "newest_code_file": "src/core/engine.py",
      "code_modified": "2025-01-10T12:00:00",
      "doc_modified": "2024-12-28T10:00:00",
      "staleness_days": 13,
      "severity": "warning",
      "suggested_action": "Update docs/api/core.md (code changed 13 days ago)"
    }
  ]
}
```

### Custom Configuration

```bash
# Use custom config file
python check_docs_freshness.py --config .docs-check-strict.json

# Override threshold globally
python check_docs_freshness.py --threshold-days 3

# Check different directory
python check_docs_freshness.py --root-dir /path/to/project
```

## Best Practices

### Mapping Rules Design

1. **Separate critical from non-critical**:
   - Use `error` severity for README, getting started guides
   - Use `warning` severity for detailed API docs

2. **Adjust thresholds by doc type**:
   - README: 1-3 days (frequently updated)
   - API docs: 7-14 days (stable interfaces)
   - Architecture docs: 14-30 days (rarely changes)

3. **Match granularity**:
   - Specific code → Specific doc (e.g., `cli.py` → `usage.md`)
   - Broad code → Broad doc (e.g., `src/**/*.py` → `docs/api/**/*.md`)

### Ignore Patterns

Exclude files that shouldn't trigger doc updates:
- Test files (`**/*_test.py`, `**/*.spec.ts`)
- Generated code (`**/__generated__/**`)
- Build artifacts (`**/dist/**`, `**/build/**`)
- Dependencies (`**/node_modules/**`, `**/vendor/**`)

### Git Integration

- **Enable** (`use_git_timestamps: true`) for most projects
- Uses last commit time, not filesystem mtime
- More accurate for repos with frequent pulls/checkouts
- **Disable** if:
  - Not a git repo
  - Git not installed in CI environment
  - Filesystem mtime preferred

### CI/CD Strategy

**Option 1: Warning Only** (recommended for starting out)
- All mappings use `severity: "warning"`
- Check runs but never fails CI
- Teams gradually update docs without pressure

**Option 2: Fail on Critical Docs**
- README/getting started = `error` severity
- API docs = `warning` severity
- Forces attention to user-facing documentation

**Option 3: Scheduled Checks**
- Run weekly via cron schedule
- Generate report as artifact
- Review during team meetings

## Troubleshooting

### Git Timestamps Not Working

**Symptom**: All files show filesystem mtime instead of git commit time

**Solutions**:
```bash
# Check git is available
git --version

# Check repo has history
git log --oneline | head

# Verify config
cat .freshness-check.json | grep use_git_timestamps

# Disable git if needed
{
  ...
  "use_git_timestamps": false
}
```

### No Files Matched

**Symptom**: "Skipping rule: no code files (0) or doc files (0)"

**Solutions**:
```bash
# Run in verbose mode
python check_docs_freshness.py --verbose

# Check patterns match files
ls -R src/**/*.py
ls -R docs/**/*.md

# Verify ignore patterns aren't too broad
cat .freshness-check.json | grep ignore_patterns
```

### False Positives

**Symptom**: Docs reported as stale when they're actually current

**Solutions**:
1. Increase `threshold_days` for that mapping
2. Exclude test files from `code_patterns`
3. Make mappings more specific (fewer files per rule)
4. Check git timestamps are working correctly

### Colorama Import Error

**Symptom**: Script works but no colored output

**Solution**:
```bash
# Optional dependency for colors
pip install colorama

# Or run without colors (automatic fallback)
python check_docs_freshness.py
```

## Advanced Usage

### Multiple Configuration Files

Maintain different configs for different strictness levels:

```bash
# Strict (for main branch)
python check_docs_freshness.py --config .docs-check-strict.json

# Lenient (for feature branches)
python check_docs_freshness.py --config .docs-check-lenient.json
```

### Custom Thresholds per Environment

**.docs-check-strict.json** (CI on main):
```json
{
    "mappings": [
        {
            "code_patterns": ["src/**/*.py"],
            "doc_patterns": ["docs/**/*.md"],
            "threshold_days": 3,
            "severity": "error"
        }
    ]
}
```

**.docs-check-lenient.json** (local development):
```json
{
    "mappings": [
        {
            "code_patterns": ["src/**/*.py"],
            "doc_patterns": ["docs/**/*.md"],
            "threshold_days": 14,
            "severity": "warning"
        }
    ]
}
```

### Integration with Linters

Add to `Makefile`:

```makefile
.PHONY: lint
lint:
	black src/
	pylint src/
	python tools/check_docs_freshness.py

.PHONY: ci
ci: lint test
	python tools/check_docs_freshness.py --json > reports/docs-freshness.json
```

## When to Use

**Use this tool if**:
- Documentation frequently gets out of sync with code
- Multiple contributors work on codebase
- Documentation is critical for users/onboarding
- You want automated reminders to update docs

**Skip this tool if**:
- Small project with single maintainer
- Documentation lives in code comments (docstrings)
- Code and docs always updated together
- Repo is documentation-only (no code to track)

## License

MIT License - Feel free to customize for your project needs.

## Dependencies

**Required**:
- Python 3.11+
- Standard library only (pathlib, subprocess, json, dataclasses)

**Optional**:
- `colorama` - Colored terminal output (graceful fallback if missing)
- `git` - For accurate commit timestamps (fallback to filesystem mtime)

## See Also

- **Pattern Library**: Project-specific patterns for development workflows
- **ADR Template**: Architecture decision records (another doc type to track)
- **CI/CD Pipeline**: Integrate freshness checks into existing workflows
