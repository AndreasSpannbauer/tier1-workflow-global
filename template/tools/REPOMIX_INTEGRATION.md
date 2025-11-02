# Repomix Integration for Repomap Generation

## Overview

**Status: EXPERIMENTAL**

Repomix integration provides optional enhancement to the proven glob-based repomap generation with:

- Tree-sitter compression (70% token reduction claimed)
- Git-aware sorting
- Multiple output formats
- Token counting

**CRITICAL**: This is an ENHANCEMENT, not a replacement. The proven glob-based implementation remains the primary method.

## Architecture

### Components

1. **RepomixAdapter** (`tools/repomix_adapter.py`)
   - Availability check
   - Scope configuration conversion
   - Error handling and fallback

2. **Config Template** (`tools/repomix_config_template.json`)
   - Reference configuration
   - Documented options

3. **Integration** (in `tools/generate_scoped_repomap.py`)
   - Engine selection: `auto`, `proven`, or `repomix`
   - Automatic fallback
   - Statistics comparison

## Installation

Repomix is NOT required for repomap generation. If you want to test it:

```bash
# Option 1: Global installation
npm install -g repomix

# Option 2: Use npx (no installation)
npx repomix@latest --version
```

## Usage

### Command Line

```bash
# Use proven engine (default, always works)
python3 tools/generate_scoped_repomap.py --scope backend

# Try Repomix (fallback to proven if unavailable)
python3 tools/generate_scoped_repomap.py --scope backend --engine auto

# Force Repomix (fails if not available)
python3 tools/generate_scoped_repomap.py --scope backend --engine repomix

# Force proven engine
python3 tools/generate_scoped_repomap.py --scope backend --engine proven
```

### Python API

```python
from pathlib import Path
from tools.repomix_adapter import RepomixAdapter, RepomixNotAvailableError

adapter = RepomixAdapter()

if adapter.is_available():
    try:
        scope_data = {
            "description": "Backend code",
            "include_patterns": ["src/**/*.py"],
            "exclude_patterns": ["**/__pycache__/**"],
            "max_file_size": 100000
        }

        output_path, stats = adapter.generate_with_repomix(
            scope_name="backend",
            scope_data=scope_data,
            output_path=Path("output.md"),
            repo_root=Path.cwd()
        )

        print(f"Generated: {output_path}")
        print(f"Files: {stats.file_count}")
        print(f"Tokens: {stats.total_tokens}")

    except RepomixFailedError as e:
        print(f"Repomix failed: {e}")
        print("Falling back to proven implementation...")
else:
    print("Repomix not available, using proven implementation")
```

## Configuration Options

### Output Configuration

```json
{
  "output": {
    "style": "markdown",        // Output format: markdown, xml, plain
    "filePath": "output.md",    // Output file path
    "showLineNumbers": true,    // Include line numbers
    "topFilesLength": 10,       // Number of top files to show
    "compress": true,           // Enable tree-sitter compression (70% reduction)
    "git": {
      "sortByChanges": true,    // Sort files by git changes
      "sortByChangesMaxCommits": 100  // Max commits to analyze
    }
  }
}
```

### Include/Exclude Patterns

```json
{
  "include": [
    "src/**/*.py",              // Glob patterns to include
    "tests/**/*.py",
    "docs/**/*.md"
  ],
  "ignore": {
    "useGitignore": true,       // Respect .gitignore
    "useDefaultPatterns": true, // Use Repomix defaults
    "customPatterns": [         // Additional exclusions
      "**/__pycache__/**",
      "**/*.pyc"
    ]
  }
}
```

### Input Constraints

```json
{
  "input": {
    "maxFileSize": 100          // Max file size in KB (not bytes!)
  }
}
```

### Security

```json
{
  "security": {
    "enableSecurityCheck": true  // Check for secrets/sensitive data
  }
}
```

## Error Handling

RepomixAdapter provides clear error handling:

```python
class RepomixError(Exception):
    """Base exception for Repomix-related errors."""
    pass

class RepomixNotAvailableError(RepomixError):
    """Raised when Repomix is not installed or not accessible."""
    pass

class RepomixFailedError(RepomixError):
    """Raised when Repomix generation fails."""
    pass
```

## Fallback Strategy

The integration implements automatic fallback:

1. **Check availability**: `adapter.is_available()`
2. **Try Repomix**: If available and requested
3. **Fallback to proven**: On any error or unavailability
4. **Always works**: Proven implementation is always available

## Statistics

RepomixAdapter tracks generation statistics:

```python
@dataclass
class RepomixStats:
    file_count: int              # Number of files processed
    total_chars: int             # Total characters
    total_tokens: int            # Estimated token count
    output_size_bytes: int       # Output file size
    compression_ratio: float     # Compression vs proven
```

## Testing Checklist

Before recommending Repomix for production:

- [ ] Repomix installs correctly
- [ ] Generation completes without errors
- [ ] Output format is usable
- [ ] Token reduction is measurable
- [ ] Performance is acceptable
- [ ] Fallback works correctly
- [ ] No security issues detected

## Known Limitations

1. **Experimental**: Not tested in production workflow
2. **External dependency**: Requires npm/npx
3. **Performance unknown**: May be slower than proven implementation
4. **Token reduction unverified**: 70% claim needs validation
5. **Config complexity**: More complex than proven implementation

## Comparison: Repomix vs Proven

| Feature | Proven Implementation | Repomix |
|---------|----------------------|---------|
| **Availability** | Always (pure Python) | Requires npm/npx |
| **Speed** | Fast (direct glob) | Unknown |
| **Token reduction** | None (raw files) | 70% claimed |
| **Git awareness** | None | Yes (sort by changes) |
| **Compression** | None | Tree-sitter |
| **Complexity** | Simple (100 LOC) | Complex (external tool) |
| **Reliability** | Proven in production | Experimental |
| **Fallback** | N/A (always works) | To proven implementation |

## Recommendation Process

1. **Test in email_management_system**
2. **Measure actual token reduction**
3. **Compare output quality**
4. **Measure performance**
5. **Document findings**
6. **Make recommendation**: Use or skip

## References

- Repomix GitHub: https://github.com/yamadashy/repomix
- Repomix Documentation: https://github.com/yamadashy/repomix/blob/main/README.md
- Config Schema: https://github.com/yamadashy/repomix/blob/main/config-schema.json
