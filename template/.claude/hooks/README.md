# Claude Code Hooks

This directory contains hooks that enhance the Tier1 workflow by capturing runtime data from Claude Code.

## capture_transcript_path.py

**Type**: UserPromptSubmit Hook
**Purpose**: Captures the conversation transcript path and makes it available to workflow commands

### Why This Hook is Required

Claude Code provides `transcript_path` (path to the session .jsonl file) to hooks via stdin JSON, but does not automatically expose it as an environment variable to slash commands. This hook bridges that gap by:

1. Receiving `transcript_path` from Claude Code in the hook's JSON input
2. Writing it to `.workflow/transcript_path.txt` for slash command access
3. Enabling the `/execute-workflow` command to export full conversation logs for post-mortem analysis

### How It Works

```
User invokes /execute-workflow
        ↓
UserPromptSubmit hook receives:
{
  "transcript_path": "/path/to/session.jsonl",
  "session_id": "...",
  "cwd": "...",
  "prompt": "..."
}
        ↓
Hook writes transcript_path to .workflow/transcript_path.txt
        ↓
Slash command reads from .workflow/transcript_path.txt
        ↓
Command exports conversation log for post-mortem
```

### Configuration

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/capture_transcript_path.py"
          }
        ]
      }
    ]
  }
}
```

### Testing

1. Invoke any slash command (e.g., `/execute-workflow EPIC-001`)
2. Check for `.workflow/transcript_path.txt`
3. Verify file contains path to `.jsonl` file
4. Verify the path points to an existing file

```bash
# Test
cat .workflow/transcript_path.txt
# Should output something like: /home/user/.claude/sessions/abc123.jsonl

# Verify file exists
ls -lh "$(cat .workflow/transcript_path.txt)"
```

### Troubleshooting

**Problem**: `.workflow/transcript_path.txt` is empty or missing

**Solutions**:
1. Verify hook is configured in `.claude/settings.json`
2. Check hook has execute permissions: `chmod +x .claude/hooks/capture_transcript_path.py`
3. Check for errors: Look for stderr output in Claude Code session
4. Verify Python 3 is available: `which python3`

**Problem**: Transcript export fails with "file not found"

**Solutions**:
1. Check that transcript path is absolute, not relative
2. Verify Claude Code has permission to read session files
3. Check that session file hasn't been deleted/cleaned up

### Impact

**With Hook Configured**:
- ✅ Full conversation logs exported to post-mortem
- ✅ Agent reasoning and decision-making visible in analysis
- ✅ Tool call history preserved
- ✅ Complete observability for workflow improvement

**Without Hook Configured**:
- ❌ Post-mortem uses placeholder instead of real conversation
- ❌ Lost context for understanding workflow execution
- ❌ Missing data for performance analysis
- ❌ Reduced organizational learning

---

**Created**: 2025-10-24
**Maintainer**: Tier1 Workflow Global
