#!/usr/bin/env python3
"""
Optional Repomix integration for enhanced repomap generation.

Falls back to proven glob-based implementation if Repomix unavailable.

EXPERIMENTAL: Repomix provides tree-sitter compression (70% token reduction)
and git-aware sorting, but requires testing before production use.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RepomixError(Exception):
    """Base exception for Repomix-related errors."""

    pass


class RepomixNotAvailableError(RepomixError):
    """Raised when Repomix is not installed or not accessible."""

    pass


class RepomixFailedError(RepomixError):
    """Raised when Repomix generation fails."""

    pass


@dataclass
class RepomixStats:
    """Statistics from Repomix generation."""

    file_count: int
    total_chars: int
    total_tokens: int
    output_size_bytes: int
    compression_ratio: float | None = None


class RepomixAdapter:
    """
    Optional Repomix integration for enhanced repomap generation.

    Provides tree-sitter compression, git-aware sorting, and token counting.
    Falls back to proven implementation if unavailable.
    """

    def __init__(self):
        """Initialize adapter and check Repomix availability."""
        self.repomix_available = self._check_repomix()

    def _check_repomix(self) -> bool:
        """
        Check if Repomix is available via npx.

        Returns:
            True if Repomix is available, False otherwise.
        """
        try:
            result = subprocess.run(
                ["npx", "repomix", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                logger.info(f"Repomix available: {result.stdout.strip()}")
                return True
            else:
                logger.warning(f"Repomix check failed: {result.stderr}")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"Repomix not available: {e}")
            return False

    def convert_scope_to_repomix_config(self, scope_name: str, scope_data: dict[str, Any]) -> dict[str, Any]:
        """
        Convert repomap scope configuration to Repomix config format.

        Args:
            scope_name: Name of the scope
            scope_data: Scope configuration dictionary with include/exclude patterns

        Returns:
            Repomix-compatible configuration dictionary
        """
        # Extract patterns from scope
        include_patterns = scope_data.get("include_patterns", [])
        exclude_patterns = scope_data.get("exclude_patterns", [])
        max_file_size = scope_data.get("max_file_size", 100000)

        # Build Repomix config
        config: dict[str, Any] = {
            "output": {
                "style": "markdown",
                "filePath": "repomix-output.md",  # Will be overridden
                "showLineNumbers": True,
                "topFilesLength": 10,
                "compress": True,  # Tree-sitter compression
                "git": {
                    "sortByChanges": True,
                    "sortByChangesMaxCommits": 100,
                },
            },
            "include": include_patterns,
            "ignore": {
                "useGitignore": True,
                "useDefaultPatterns": True,
                "customPatterns": exclude_patterns,
            },
            "security": {
                "enableSecurityCheck": True,
            },
        }

        # Add file size limit (convert bytes to KB for Repomix)
        if max_file_size:
            config["input"] = {"maxFileSize": max_file_size // 1024}

        return config

    def _write_temp_config(self, config: dict[str, Any]) -> Path:
        """
        Write Repomix config to temporary file.

        Args:
            config: Repomix configuration dictionary

        Returns:
            Path to temporary config file
        """
        temp_file = Path(tempfile.mktemp(suffix=".json", prefix="repomix-config-"))
        temp_file.write_text(json.dumps(config, indent=2))
        logger.debug(f"Wrote Repomix config to {temp_file}")
        return temp_file

    def generate_with_repomix(
        self, scope_name: str, scope_data: dict[str, Any], output_path: Path, repo_root: Path
    ) -> tuple[Path, RepomixStats]:
        """
        Generate repomap using Repomix (EXPERIMENTAL).

        Args:
            scope_name: Name of the scope being generated
            scope_data: Scope configuration dictionary
            output_path: Where to write the output
            repo_root: Repository root directory

        Returns:
            Tuple of (output_path, stats)

        Raises:
            RepomixNotAvailableError: If Repomix not installed
            RepomixFailedError: If generation fails
        """
        if not self.repomix_available:
            raise RepomixNotAvailableError(
                "Repomix not available. Install: npm install -g repomix\n"
                "Or use npx: npx repomix@latest"
            )

        # Generate config
        config = self.convert_scope_to_repomix_config(scope_name, scope_data)

        # Override output path in config
        config["output"]["filePath"] = str(output_path)

        # Write config to temp file
        config_path = self._write_temp_config(config)

        try:
            # Run Repomix
            logger.info(f"Running Repomix for scope '{scope_name}'...")

            result = subprocess.run(
                [
                    "npx",
                    "repomix",
                    "--config",
                    str(config_path),
                    "--style",
                    "markdown",
                    "--compress",
                    "--output",
                    str(output_path),
                    str(repo_root),
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,
                cwd=repo_root,
            )

            if result.returncode != 0:
                raise RepomixFailedError(f"Repomix generation failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")

            # Parse stats from output if available
            stats = self._parse_repomix_output(result.stdout, output_path)

            logger.info(f"Repomix generation complete: {output_path}")
            return output_path, stats

        except subprocess.TimeoutExpired as e:
            raise RepomixFailedError(f"Repomix generation timed out after 5 minutes: {e}")
        except Exception as e:
            raise RepomixFailedError(f"Unexpected error during Repomix generation: {e}")
        finally:
            # Clean up temp config
            try:
                config_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to clean up temp config: {e}")

    def _parse_repomix_output(self, stdout: str, output_path: Path) -> RepomixStats:
        """
        Parse statistics from Repomix output.

        Args:
            stdout: Repomix stdout
            output_path: Path to generated file

        Returns:
            RepomixStats with parsed statistics
        """
        # Try to extract stats from stdout
        file_count = 0
        total_chars = 0
        total_tokens = 0

        # Look for patterns in Repomix output
        # Example: "  Total Files: 586 files"
        # Example: " Total Tokens: 662,856 tokens"
        # Example: "  Total Chars: 2,796,312 chars"
        for line in stdout.splitlines():
            line_stripped = line.strip()

            if line_stripped.startswith("Total Files:"):
                try:
                    # Extract number before "files"
                    parts = line_stripped.split(":")
                    if len(parts) >= 2:
                        number_str = parts[1].strip().split()[0].replace(",", "")
                        file_count = int(number_str)
                except (ValueError, IndexError):
                    pass

            elif line_stripped.startswith("Total Chars:"):
                try:
                    parts = line_stripped.split(":")
                    if len(parts) >= 2:
                        number_str = parts[1].strip().split()[0].replace(",", "")
                        total_chars = int(number_str)
                except (ValueError, IndexError):
                    pass

            elif line_stripped.startswith("Total Tokens:"):
                try:
                    parts = line_stripped.split(":")
                    if len(parts) >= 2:
                        number_str = parts[1].strip().split()[0].replace(",", "")
                        total_tokens = int(number_str)
                except (ValueError, IndexError):
                    pass

        # Get output file size
        output_size = 0
        if output_path.exists():
            output_size = output_path.stat().st_size

        return RepomixStats(
            file_count=file_count,
            total_chars=total_chars,
            total_tokens=total_tokens,
            output_size_bytes=output_size,
        )

    def is_available(self) -> bool:
        """
        Check if Repomix is currently available.

        Returns:
            True if available, False otherwise
        """
        return self.repomix_available


def main():
    """Test Repomix adapter."""
    logging.basicConfig(level=logging.INFO)

    adapter = RepomixAdapter()

    if adapter.is_available():
        print("✅ Repomix is available")

        # Example scope
        test_scope = {
            "description": "Backend Python code",
            "include_patterns": ["src/**/*.py", "tests/**/*.py"],
            "exclude_patterns": ["**/__pycache__/**", "**/*.pyc"],
            "max_file_size": 100000,
        }

        config = adapter.convert_scope_to_repomix_config("test", test_scope)
        print("\n📋 Generated Repomix config:")
        print(json.dumps(config, indent=2))
    else:
        print("❌ Repomix not available")
        print("Install with: npm install -g repomix")
        print("Or use npx: npx repomix@latest")


if __name__ == "__main__":
    main()
