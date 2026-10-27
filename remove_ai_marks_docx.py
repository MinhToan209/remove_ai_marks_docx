#!/usr/bin/env python3
"""Remove common provenance/metadata marks from a DOCX file.

This removes document properties and suspicious invisible Unicode characters from
Word XML. It does not prove human authorship and does not rewrite prose.

Usage:
    python remove_ai_marks_docx.py input.docx output.docx
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path


# Characters commonly used as invisible text markers. ZWJ/ZWNJ are intentionally
# excluded because they can be meaningful in emoji and some writing systems.
INVISIBLE_RE = re.compile(
    "[\u0000\u0008\u000b\u000c\u000e-\u001f\u007f\u00ad\u034f"
    "\u061c\u115f\u1160\u17b4\u17b5\u180e\u200b\u200e\u200f"
    "\u202a-\u202e\u2060-\u2064\u2066-\u206f\u206a-\u206f\ufeff\ufff9-\ufffb]"
)

CORE_PROPS = "docProps/core.xml"
APP_PROPS = "docProps/app.xml"
CUSTOM_PROPS = "docProps/custom.xml"

EMPTY_CUSTOM_PROPS = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"/>'''


def clean_xml_bytes(data: bytes) -> tuple[bytes, int]:
    text = data.decode("utf-8")
    cleaned, count = INVISIBLE_RE.subn("", text)
    return cleaned.encode("utf-8"), count


def clear_property_values(data: bytes) -> bytes:
    """Blank core/app property values without removing package parts."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(data)
    for element in root.iter():
        if element is not root and element.text:
            element.text = None
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def scrub_docx(source: Path, destination: Path) -> tuple[int, list[str]]:
    if source.resolve() == destination.resolve():
        raise ValueError("input and output must be different files")
    if source.suffix.lower() != ".docx":
        raise ValueError("input must be a .docx file")

    destination.parent.mkdir(parents=True, exist_ok=True)
    changed_chars = 0
    changed_parts: list[str] = []

    with zipfile.ZipFile(source, "r") as zin:
        names = zin.namelist()
        if "[Content_Types].xml" not in names or "word/document.xml" not in names:
            raise ValueError("input does not appear to be a valid DOCX file")

        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename == CUSTOM_PROPS:
                    data = EMPTY_CUSTOM_PROPS
                    changed_parts.append(item.filename)
                elif item.filename in (CORE_PROPS, APP_PROPS):
                    # Blank author/company/title/etc. while preserving the
                    # package parts and their relationships.
                    data = clear_property_values(data)
                    changed_parts.append(item.filename)
                elif item.filename.startswith("docProps/") and item.filename.endswith(".xml"):
                    data, count = clean_xml_bytes(data)
                    changed_chars += count
                    if count:
                        changed_parts.append(item.filename)
                elif item.filename.endswith(".xml") or item.filename.endswith(".rels"):
                    data, count = clean_xml_bytes(data)
                    changed_chars += count
                    if count:
                        changed_parts.append(item.filename)

                zout.writestr(item, data)

    return changed_chars, sorted(set(changed_parts))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove common DOCX metadata and invisible Unicode markers."
    )
    parser.add_argument("input", type=Path, help="input .docx path")
    parser.add_argument("output", type=Path, help="output .docx path")
    args = parser.parse_args()

    try:
        if not args.input.is_file():
            raise ValueError(f"input file not found: {args.input}")
        chars, parts = scrub_docx(args.input, args.output)
    except (OSError, zipfile.BadZipFile, ValueError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created: {args.output}")
    print(f"Invisible characters removed: {chars}")
    print(f"Metadata/custom-property parts processed: {len(parts)}")
    if parts:
        for part in parts:
            print(f"  - {part}")
    print("Note: this does not remove statistical AI-detector signals or prove authorship.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
