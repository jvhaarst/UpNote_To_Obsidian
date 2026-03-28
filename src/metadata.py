from __future__ import annotations

import frontmatter


def extract_metadata(md_content: str) -> dict:
    """Parse YAML frontmatter from UpNote MD export content.

    Returns dict with 'date', 'created', and 'categories' keys.
    """
    post = frontmatter.loads(md_content)
    return {
        "date": str(post.get("date", "")),
        "created": str(post.get("created", "")),
        "categories": list(post.get("categories", [])),
    }


def detect_space_name(all_categories: list[list[str]]) -> str | None:
    """Find the category that appears in every single note.

    This is the UpNote 'space' name which carries no useful information.
    Returns None if no universal category exists.
    """
    if not all_categories:
        return None
    common = set(all_categories[0])
    for cats in all_categories[1:]:
        common &= set(cats)
    if len(common) == 1:
        return common.pop()
    return None
