#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Capture Transcript Path

This hook captures the transcript_path from Claude Code and makes it available
to slash commands by writing it to a well-known location.

The transcript_path is required for workflow post-mortem analysis to export
the full conversation history.

Created: 2025-10-24
"""

import json
import sys
from pathlib import Path


def main():
    """Capture transcript_path and write to file for slash command access."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        # Extract transcript_path from hook input
        transcript_path = input_data.get('transcript_path', '')

        if transcript_path:
            # Write to workflow directory for slash command access
            workflow_dir = Path('.workflow')
            workflow_dir.mkdir(parents=True, exist_ok=True)

            transcript_path_file = workflow_dir / 'transcript_path.txt'
            transcript_path_file.write_text(transcript_path, encoding='utf-8')

            # Silent success - no output to avoid cluttering conversation
            # Only output on failure for debugging
        else:
            # If no transcript_path, write empty file to signal availability check failed
            workflow_dir = Path('.workflow')
            workflow_dir.mkdir(parents=True, exist_ok=True)

            transcript_path_file = workflow_dir / 'transcript_path.txt'
            transcript_path_file.write_text('', encoding='utf-8')

        sys.exit(0)  # Success

    except Exception as e:
        # Silent failure - we don't want to block Claude Code execution
        # Just log to stderr for debugging if needed
        print(f"Warning: transcript_path capture failed: {e}", file=sys.stderr)
        sys.exit(0)  # Exit successfully to avoid blocking


if __name__ == "__main__":
    main()
