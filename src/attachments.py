from __future__ import annotations

import re
from urllib.parse import unquote

from bs4 import BeautifulSoup


def extract_attachment_refs(html_content: str) -> list[str]:
    """Extract all local attachment references from HTML.

    Finds <img src="Files/..."> and <a href="Files/..."> references.
    Returns URL-decoded file paths.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    refs: list[str] = []

    for img in soup.find_all("img", src=True):
        src = img["src"]
        if src.startswith("Files/"):
            refs.append(unquote(src))

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("Files/"):
            refs.append(unquote(href))

    return refs


def rewrite_attachment_paths(md_content: str) -> str:
    """Rewrite Files/ references in markdown to attachments/ paths.

    Handles both ![](Files/...) image refs and [text](Files/...) link refs.
    Preserves URL-encoding so paths with spaces render correctly in Obsidian.
    """

    def replace_files_ref(match: re.Match) -> str:
        prefix = match.group(1)  # "![...](" or "[...]("
        path = match.group(2)  # "Files/..."
        suffix = match.group(3)  # ")"
        new_path = path.replace("Files/", "attachments/", 1)
        return f"{prefix}{new_path}{suffix}"

    # Match ![...](Files/...) and [...](Files/...)
    pattern = r"(!?\[[^\]]*\]\()(Files/[^)]+)(\))"
    return re.sub(pattern, replace_files_ref, md_content)
