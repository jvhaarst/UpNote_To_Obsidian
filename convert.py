#!/usr/bin/env python3
"""UpNote to Obsidian converter.

Usage:
    uv run python convert.py --html-dir <path> --md-dir <path> --output-dir <path>
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from src.attachments import extract_attachment_refs, rewrite_attachment_paths
from src.html_converter import convert_html
from src.metadata import detect_space_name, extract_metadata
from src.writer import build_frontmatter, determine_output_path


def find_notes(html_dir: Path, md_dir: Path) -> list[tuple[str, Path, Path]]:
    """Find matching HTML/MD pairs. Returns list of (name, html_path, md_path)."""
    html_files = {p.stem: p for p in html_dir.glob("*.html")}
    md_files = {p.stem: p for p in md_dir.glob("*.md")}
    common = sorted(html_files.keys() & md_files.keys())
    return [(name, html_files[name], md_files[name]) for name in common]


def detect_space(notes: list[tuple[str, Path, Path]]) -> str | None:
    """Read all MD files to detect the universal space name."""
    all_categories = []
    for _name, _html_path, md_path in notes:
        meta = extract_metadata(md_path.read_text(encoding="utf-8"))
        if meta["categories"]:
            all_categories.append(meta["categories"])
    return detect_space_name(all_categories)


def process_note(
    name: str,
    html_path: Path,
    md_path: Path,
    html_files_dir: Path,
    space_name: str | None,
    output_dir: Path,
) -> dict:
    """Process a single note. Returns stats dict."""
    stats = {"converted": False, "images_copied": 0, "warnings": []}

    # 1. Extract metadata from MD
    md_content = md_path.read_text(encoding="utf-8")
    meta = extract_metadata(md_content)

    # 2. Read and convert HTML
    html_content = html_path.read_text(encoding="utf-8")
    markdown = convert_html(html_content)

    # 3. Extract attachment references from HTML
    attachment_refs = extract_attachment_refs(html_content)
    has_attachments = len(attachment_refs) > 0

    # 4. Determine output path
    out_path = determine_output_path(
        note_name=name,
        categories=meta["categories"],
        space_name=space_name,
        has_attachments=has_attachments,
        output_dir=output_dir,
    )

    # 5. Handle filename conflicts
    if out_path.exists():
        counter = 2
        while True:
            stem = f"{name} ({counter})"
            if has_attachments:
                candidate = out_path.parent.parent / stem / f"{stem}.md"
            else:
                candidate = out_path.parent / f"{stem}.md"
            if not candidate.exists():
                out_path = candidate
                break
            counter += 1

    # 6. Create output directories
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 7. Copy attachments
    if has_attachments:
        attachments_dir = out_path.parent / "attachments"
        attachments_dir.mkdir(exist_ok=True)
        for ref in attachment_refs:
            src_file = html_files_dir / ref.replace("Files/", "", 1)
            if src_file.exists():
                shutil.copy2(src_file, attachments_dir / src_file.name)
                stats["images_copied"] += 1
            else:
                stats["warnings"].append(f"Missing attachment: {ref} for note {name}")

    # 8. Rewrite attachment paths in markdown
    markdown = rewrite_attachment_paths(markdown)

    # 9. Build frontmatter and write
    frontmatter = build_frontmatter(
        created=meta["created"],
        categories=meta["categories"],
        space_name=space_name,
    )

    out_path.write_text(frontmatter + "\n" + markdown, encoding="utf-8")
    stats["converted"] = True
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert UpNote exports to Obsidian vault")
    parser.add_argument(
        "--html-dir",
        type=Path,
        required=True,
        help="Path to HTML export General Space/ directory",
    )
    parser.add_argument(
        "--md-dir",
        type=Path,
        required=True,
        help="Path to MD export General Space/ directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("obsidian_vault"),
        help="Output directory for vault",
    )
    args = parser.parse_args()

    html_dir = args.html_dir
    md_dir = args.md_dir
    output_dir = args.output_dir

    # Validate inputs
    if not html_dir.is_dir():
        print(f"Error: HTML directory not found: {html_dir}", file=sys.stderr)
        sys.exit(1)
    if not md_dir.is_dir():
        print(f"Error: MD directory not found: {md_dir}", file=sys.stderr)
        sys.exit(1)

    html_files_dir = html_dir / "Files"

    # Find matching note pairs
    notes = find_notes(html_dir, md_dir)
    if not notes:
        print("No matching HTML/MD pairs found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(notes)} notes to convert")

    # Detect space name
    space_name = detect_space(notes)
    if space_name:
        print(f"Detected space name: '{space_name}' (will be excluded from tags)")

    # Process each note
    total_converted = 0
    total_skipped = 0
    total_images = 0
    all_warnings: list[str] = []

    for name, html_path, md_path in notes:
        try:
            stats = process_note(name, html_path, md_path, html_files_dir, space_name, output_dir)
            if stats["converted"]:
                total_converted += 1
            total_images += stats["images_copied"]
            all_warnings.extend(stats["warnings"])
        except Exception as e:
            total_skipped += 1
            print(f"WARNING: Failed to convert '{name}': {e}", file=sys.stderr)

    # Print warnings
    for warning in all_warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    # Summary
    print(f"\nConverted: {total_converted} notes")
    if total_skipped:
        print(f"Skipped: {total_skipped} notes (see warnings above)")
    print(f"Images copied: {total_images}")
    print(f"Output: {output_dir}/")


if __name__ == "__main__":
    main()
