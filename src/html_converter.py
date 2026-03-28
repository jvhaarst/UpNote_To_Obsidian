from __future__ import annotations

import re

from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import MarkdownConverter


class UpNoteConverter(MarkdownConverter):
    """Custom markdownify converter for UpNote HTML -> Obsidian markdown."""

    def convert_pre(self, el: Tag, text: str, **kwargs: object) -> str:
        """Convert <pre> blocks to fenced code blocks with <br> as newlines."""
        # Extract raw text content, converting <br> to newlines
        lines = []
        for child in el.children:
            if isinstance(child, NavigableString):
                lines.append(str(child))
            elif isinstance(child, Tag) and child.name == "br":
                lines.append("\n")
            else:
                lines.append(child.get_text())
        code = "".join(lines).strip("\n")
        return f"\n\n```\n{code}\n```\n\n"

    def convert_table(self, el: Tag, text: str, **kwargs: object) -> str:
        """Convert <table> to markdown table."""
        rows = el.find_all("tr")
        if not rows:
            return text

        table_data: list[list[str]] = []

        for row in rows:
            cells = row.find_all(["th", "td"])
            row_data = []
            for cell in cells:
                # Get cell text, collapse internal whitespace and <br>
                cell_text = cell.get_text(separator=" ").strip()
                cell_text = re.sub(r"\s+", " ", cell_text)
                row_data.append(cell_text)
            table_data.append(row_data)

        if not table_data:
            return text

        # First row is always treated as header
        result_lines = []
        header = table_data[0]
        result_lines.append("| " + " | ".join(header) + " |")
        result_lines.append("| " + " | ".join("---" for _ in header) + " |")

        for row in table_data[1:]:
            # Pad row if needed
            while len(row) < len(header):
                row.append("")
            result_lines.append("| " + " | ".join(row) + " |")

        return "\n\n" + "\n".join(result_lines) + "\n\n"

    # Prevent markdownify from processing table internals
    def convert_td(self, el: Tag, text: str, **kwargs: object) -> str:
        return text

    def convert_th(self, el: Tag, text: str, **kwargs: object) -> str:
        return text

    def convert_tr(self, el: Tag, text: str, **kwargs: object) -> str:
        return text

    def convert_thead(self, el: Tag, text: str, **kwargs: object) -> str:
        return text

    def convert_tbody(self, el: Tag, text: str, **kwargs: object) -> str:
        return text

    def convert_colgroup(self, el: Tag, text: str, **kwargs: object) -> str:
        return ""


def convert_html(html_content: str) -> str:
    """Convert UpNote HTML export to Obsidian-compatible markdown.

    Extracts the content from the <div class="shine-editor"> wrapper if present,
    strips styling, and converts to clean markdown.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract content from shine-editor wrapper if present
    editor = soup.find("div", class_="shine-editor")
    if editor:
        target = editor
    elif soup.body:
        target = soup.body
    else:
        target = soup

    # Strip style attributes from all elements
    for tag in target.find_all(True):
        if tag.attrs:
            tag.attrs = {k: v for k, v in tag.attrs.items() if k not in ("style", "class", "data-keep-colors")}

    # Convert to markdown
    md = UpNoteConverter(
        heading_style="atx",
        bullets="*",
        strip=["head", "colgroup"],
    ).convert(str(target))

    # Collapse excessive newlines (more than 2 consecutive) to max 2
    md = re.sub(r"\n{3,}", "\n\n", md)

    return md.strip() + "\n"
