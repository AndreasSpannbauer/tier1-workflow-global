#!/usr/bin/env python3
"""
PDF Generation Module

Converts text files to optimized PDFs using enscript and ps2pdf.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def convert_to_pdf(txt_file: Path, pdf_file: Path) -> bool:
    """
    Convert text file to optimized PDF using enscript and ps2pdf.
    Returns True on success, False on failure.
    """
    try:
        # Step 1: Convert to PostScript with enscript (small font, no header)
        ps_file = txt_file.parent / f"{txt_file.stem}.ps"

        print("🔄 Converting to PostScript...")
        enscript_result = subprocess.run(
            [
                "enscript",
                "-B",  # No header
                "-f",
                "Courier4",  # 4pt font for compact output
                "--word-wrap",  # Wrap long lines
                "--media=A4",  # A4 paper size
                "-o",
                str(ps_file),
                str(txt_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if enscript_result.returncode != 0:
            print(f"⚠️  enscript warning (continuing): {enscript_result.stderr[:200]}")

        if not ps_file.exists():
            print("❌ PostScript file not created")
            return False

        # Step 2: Convert PostScript to compressed PDF
        print("🔄 Converting to compressed PDF...")
        subprocess.run(
            [
                "ps2pdf",
                "-dPDFSETTINGS=/ebook",  # Optimize for small file size
                "-dCompressPages=true",
                "-dUseFlateCompression=true",
                str(ps_file),
                str(pdf_file),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Clean up PostScript file
        ps_file.unlink()

        if not pdf_file.exists():
            print("❌ PDF file not created")
            return False

        # Check size
        pdf_size_mb = pdf_file.stat().st_size / (1024 * 1024)
        print(f"✅ PDF created: {pdf_file.name} ({pdf_size_mb:.2f} MB)")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ PDF conversion failed: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Required tool not found: {e}")
        print("   Install with: sudo apt-get install enscript ghostscript")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during PDF conversion: {e}")
        return False
