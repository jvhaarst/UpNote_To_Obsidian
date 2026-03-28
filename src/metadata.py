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
    """Detect the UpNote space name from category lists.

    The space name is the most common first category across all notes,
    present in more than half of the notes that have categories.
    Returns None if no such dominant category exists.
    """
    if not all_categories:
        return None
    from collections import Counter

    first_cats = Counter(cats[0] for cats in all_categories if cats)
    if not first_cats:
        return None
    most_common, count = first_cats.most_common(1)[0]
    if count > len(all_categories) / 2:
        return most_common
    return None
