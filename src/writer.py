from __future__ import annotations

from pathlib import Path


def determine_output_path(
    note_name: str,
    categories: list[str],
    space_name: str | None,
    has_attachments: bool,
    output_dir: Path,
) -> Path:
    """Determine the output file path for a note.

    Uses the first non-space category as the folder name.
    Notes with attachments get their own subfolder.
    Notes with no category go to _uncategorized/.
    """
    tags = [c for c in categories if c != space_name]
    folder = tags[0] if tags else "_uncategorized"

    if has_attachments:
        return output_dir / folder / note_name / f"{note_name}.md"
    return output_dir / folder / f"{note_name}.md"


def build_frontmatter(
    created: str,
    categories: list[str],
    space_name: str | None,
) -> str:
    """Build YAML frontmatter string for an Obsidian note."""
    # Convert date format: "2014-07-09 16:47:38" -> "2014-07-09T16:47:38"
    date_str = created.replace(" ", "T") if created else ""

    tags = [c for c in categories if c != space_name]

    lines = ["---"]
    lines.append(f"date: {date_str}")

    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {tag}")
    else:
        lines.append("tags: []")

    lines.append("aliases: []")
    lines.append("---")

    return "\n".join(lines) + "\n"
