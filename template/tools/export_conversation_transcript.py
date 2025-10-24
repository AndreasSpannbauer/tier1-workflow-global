#!/usr/bin/env python3
"""
Universal Conversation Transcript Exporter

Parses Claude Code session transcript JSONL files and exports as markdown.
Works for both Tier1 and V6 workflows - no MCP dependency.

Usage:
    python3 export_conversation_transcript.py <transcript_path> <output_path>

Created: 2025-10-22
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_message_content(content: Any) -> List[Dict[str, str]]:
    """
    Parse message content blocks from transcript.

    Args:
        content: Message content (string or list of blocks)

    Returns:
        List of parsed content blocks
    """
    blocks = []

    if isinstance(content, str):
        blocks.append({"type": "text", "text": content})
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                blocks.append(block)
            elif isinstance(block, str):
                blocks.append({"type": "text", "text": block})

    return blocks


def format_timestamp(timestamp_str: Optional[str]) -> str:
    """Format ISO timestamp to readable format."""
    if not timestamp_str:
        return "unknown"

    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp_str


def parse_transcript_to_markdown(transcript_path: str) -> str:
    """
    Parse Claude Code JSONL transcript and convert to markdown.

    Args:
        transcript_path: Path to .jsonl transcript file

    Returns:
        Markdown-formatted conversation log
    """
    transcript_file = Path(transcript_path)

    if not transcript_file.exists():
        return f"# Error\n\nTranscript file not found: {transcript_path}"

    markdown_lines = [
        "# Conversation Transcript",
        "",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Source:** {transcript_path}",
        "",
        "---",
        ""
    ]

    message_count = 0
    tool_call_count = 0

    try:
        with open(transcript_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    markdown_lines.append(f"<!-- Skipped malformed JSON at line {line_num}: {e} -->")
                    continue

                # Extract message data
                if 'message' not in entry:
                    continue

                msg = entry['message']
                role = msg.get('role', 'unknown')
                message_id = msg.get('id', 'unknown')
                timestamp = entry.get('timestamp')
                formatted_time = format_timestamp(timestamp)

                # User messages
                if role == 'user':
                    message_count += 1
                    content_blocks = parse_message_content(msg.get('content', []))

                    for block in content_blocks:
                        block_type = block.get('type', 'unknown')

                        if block_type == 'text':
                            text = block.get('text', '').strip()
                            if text:
                                markdown_lines.extend([
                                    f"## 👤 User Message #{message_count}",
                                    f"**Time:** {formatted_time}",
                                    "",
                                    text,
                                    "",
                                    "---",
                                    ""
                                ])

                        elif block_type == 'tool_result':
                            tool_use_id = block.get('tool_use_id', 'unknown')
                            result_content = block.get('content', '')

                            markdown_lines.extend([
                                f"### 🔧 Tool Result",
                                f"**Tool Use ID:** `{tool_use_id}`",
                                f"**Time:** {formatted_time}",
                                "",
                                "```",
                                str(result_content)[:1000],  # Limit to 1000 chars
                                "```",
                                "",
                            ])

                # Assistant messages
                elif role == 'assistant':
                    message_count += 1
                    content_blocks = parse_message_content(msg.get('content', []))

                    text_blocks = []
                    tool_uses = []
                    thinking_blocks = []

                    for block in content_blocks:
                        block_type = block.get('type', 'unknown')

                        if block_type == 'text':
                            text_blocks.append(block.get('text', ''))
                        elif block_type == 'tool_use':
                            tool_uses.append(block)
                        elif block_type == 'thinking':
                            thinking_blocks.append(block.get('thinking', ''))

                    # Output assistant message header
                    markdown_lines.extend([
                        f"## 🤖 Assistant Response #{message_count}",
                        f"**Time:** {formatted_time}",
                        f"**Message ID:** `{message_id}`",
                        ""
                    ])

                    # Thinking (if enabled)
                    if thinking_blocks:
                        thinking_text = '\n\n'.join(thinking_blocks)
                        markdown_lines.extend([
                            "### 💭 Thinking",
                            "",
                            "<details>",
                            "<summary>Show reasoning</summary>",
                            "",
                            "```",
                            thinking_text[:2000],  # Limit thinking to 2000 chars
                            "```",
                            "",
                            "</details>",
                            ""
                        ])

                    # Text response
                    if text_blocks:
                        response_text = '\n\n'.join(text_blocks)
                        markdown_lines.extend([
                            response_text,
                            ""
                        ])

                    # Tool calls
                    if tool_uses:
                        markdown_lines.append("### 🛠️ Tool Calls")
                        markdown_lines.append("")

                        for tool in tool_uses:
                            tool_call_count += 1
                            tool_name = tool.get('name', 'unknown')
                            tool_input = tool.get('input', {})
                            tool_id = tool.get('id', 'unknown')

                            markdown_lines.extend([
                                f"**{tool_call_count}. {tool_name}**",
                                f"- Tool ID: `{tool_id}`",
                                "",
                                "```json",
                                json.dumps(tool_input, indent=2)[:500],  # Limit to 500 chars
                                "```",
                                ""
                            ])

                    markdown_lines.extend(["---", ""])

    except Exception as e:
        markdown_lines.extend([
            "",
            "## ❌ Error Parsing Transcript",
            "",
            f"Error: {str(e)}",
            "",
            "The transcript may be incomplete or corrupted."
        ])

    # Summary footer
    markdown_lines.extend([
        "",
        "---",
        "",
        "## 📊 Transcript Summary",
        "",
        f"- **Total Messages:** {message_count}",
        f"- **Tool Calls:** {tool_call_count}",
        f"- **Transcript File:** `{transcript_path}`",
        ""
    ])

    return "\n".join(markdown_lines)


def export_conversation_log(
    transcript_path: str,
    output_path: str,
    epic_id: Optional[str] = None
) -> bool:
    """
    Export Claude Code conversation transcript as markdown.

    Args:
        transcript_path: Path to .jsonl transcript from hook input
        output_path: Path to write markdown output
        epic_id: Optional epic ID for metadata

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n[Transcript Export] Parsing {transcript_path}...")

        # Parse transcript
        markdown_content = parse_transcript_to_markdown(transcript_path)

        # Add epic ID if provided
        if epic_id:
            markdown_content = markdown_content.replace(
                "# Conversation Transcript",
                f"# Conversation Transcript: {epic_id}"
            )

        # Write output
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(markdown_content, encoding='utf-8')

        print(f"✅ Conversation transcript exported: {output_path}")
        print(f"   Size: {len(markdown_content)} characters")

        return True

    except Exception as e:
        print(f"❌ Failed to export conversation transcript: {e}")
        return False


def main():
    """CLI interface for standalone execution."""
    if len(sys.argv) < 3:
        print("Usage: python3 export_conversation_transcript.py <transcript_path> <output_path> [epic_id]")
        print("\nExport Claude Code conversation transcript as markdown.")
        print("\nArguments:")
        print("  transcript_path  Path to .jsonl transcript file")
        print("  output_path      Path to write markdown output")
        print("  epic_id          Optional epic ID for metadata")
        sys.exit(1)

    transcript_path = sys.argv[1]
    output_path = sys.argv[2]
    epic_id = sys.argv[3] if len(sys.argv) > 3 else None

    success = export_conversation_log(transcript_path, output_path, epic_id)

    if success:
        print(f"\n✅ Transcript export successful")
        sys.exit(0)
    else:
        print(f"\n❌ Transcript export failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
